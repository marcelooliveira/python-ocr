import json
import os
from statistics import median
from decimal import Decimal
from MongoDBHelper import MongoDBHelper
import azure.ai.vision as sdk
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

def process_ocr(source_image):
  service_options = sdk.VisionServiceOptions(os.environ["VISION_ENDPOINT"],
                       os.environ["VISION_KEY"])

  vision_source = sdk.VisionSource(filename=source_image)

  analysis_options = sdk.ImageAnalysisOptions()

  analysis_options.features = (
    sdk.ImageAnalysisFeature.CAPTION |
    sdk.ImageAnalysisFeature.TEXT
  )

  analysis_options.language = "en"

  analysis_options.gender_neutral_caption = True

  image_analyzer = sdk.ImageAnalyzer(service_options, vision_source, analysis_options)

  result = image_analyzer.analyze()

  base_file_name, ext = source_image.split('.')
  result_file = '{}.{}'.format(base_file_name, 'json')

  analysis_result = { "file_name": result_file }

  string_list = []

  if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:

    if result.caption is not None:
        print(" Caption:", flush=True)
        print("   '{}', Confidence {:.4f}".format(result.caption.content, result.caption.confidence), flush=True)
        analysis_result["caption"] = { 
                                      "content": result.caption.content,
                                      "confidence": result.caption.confidence
                                      }
        
        analysis_result["text"] = {
                                      "lines": []
                                  }

    if result.text is not None:
      print(" Text:", flush=True)      
      for line in result.text.lines:
        points_string = ("{" +
        ", ".join([str(int(point)) for point in line.bounding_polygon]) + 
        "}")
        print("   Line: '{}', Bounding polygon {}".format(line.content, points_string), flush=True)
        line_result = {
                        "content": line.content,
                        "bounding_polygon": line.bounding_polygon,
                        "words": [],
                      }

        for word in line.words:
          word_result = {
                          "content": word.content,
                          "bounding_polygon": word.bounding_polygon,
                          "confidence": word.confidence
                        }
          points_string = ("{" +
                   ", ".join([str(int(p)) for p in word.bounding_polygon]) +
                   "}")
          print("     Word: '{}', Bounding polygon {}, Confidence {:.4f}"
                .format(word.content, points_string, word.confidence), flush=True)
          string_list.append(word.content)
          line_result["words"].append(word_result)

        analysis_result["text"]["lines"].append(line_result)

      local_file_path = result_file
      results_file = open(local_file_path, "w")
      results_file.write(json.dumps(analysis_result))
      results_file.close()

      inserted_id = insert_document(analysis_result)

      number_list = convert_to_decimal_list(string_list)

      aggregate_result = aggregate_operations(number_list)

      # Your Azure Cosmos DB Table API connection string
      insert_entity(inserted_id, aggregate_result)

      return aggregate_result

  else:
    error_details = sdk.ImageAnalysisErrorDetails.from_result(result)

    return error_details

def insert_entity(inserted_id, aggregate_result):
    connection_string = os.environ["TABLE_DB_CONNECTION_STRING"]

      # Create a TableService client
    table_service = TableService(connection_string=connection_string)

      # Define your data structure
    data = Entity()
    data.PartitionKey = "data_partition"
    data.RowKey = inserted_id
    data.sum = float(aggregate_result["sum"])
    data.average = float(aggregate_result["average"])
    data.median = float(aggregate_result["median"])
    data.min = float(aggregate_result["min"])
    data.max = float(aggregate_result["max"])

      # Insert the entity into the table
    table_service.insert_entity('AggregateResults', data)

def insert_document(analysis_result):
    connection_string = os.environ["MONGO_DB_CONNECTION_STRING"]
    db_name = os.environ["MONGO_DB_NAME"]
    collection_name = os.environ["MONGO_COLLECTION_ID"]

    db_helper = MongoDBHelper(connection_string, db_name, collection_name)

    inserted_id = db_helper.create_document(analysis_result)
    print("Inserted document ID:", str(inserted_id))
    return str(inserted_id)

def convert_to_decimal_list(string_list):
  return list(map(Decimal, string_list))

def aggregate_operations(numbers):
  result = {
    'sum': sum(numbers),
    'average': sum(numbers) / len(numbers),
    'median': median(numbers),
    'min': min(numbers),
    'max': max(numbers)
  }
  return result
