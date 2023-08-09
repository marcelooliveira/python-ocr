import json
import os
from statistics import median
from decimal import Decimal
from CosmosDBHelper import CosmosDBHelper
import azure.ai.vision as sdk

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
        document_id = os.path.basename(source_image).rsplit('.', 1)[0]
        analysis_result["id"] = document_id
        analysis_result["partitionKey"] = "Partition1"

      local_file_path = result_file
      results_file = open(local_file_path, "w")
      results_file.write(json.dumps(analysis_result))
      results_file.close()

      inserted_id = insert_analysis(analysis_result)

      number_list = convert_to_decimal_list(string_list)

      aggregate_result = aggregate_operations(number_list)

      insert_aggregate_result(inserted_id, aggregate_result)
      return aggregate_result

  else:
    return sdk.ImageAnalysisErrorDetails.from_result(result)

def insert_aggregate_result(inserted_id, aggregate_result):
    db_helper = CosmosDBHelper()
    db_helper.create_aggregate_result(inserted_id, aggregate_result)

def insert_analysis(analysis_result):
    db_helper = CosmosDBHelper()
    doc = db_helper.create_analysis(analysis_result)
    return str(doc["id"])

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
