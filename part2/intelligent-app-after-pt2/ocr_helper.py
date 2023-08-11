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

  ocr_result = get_ocr_result(result)
  analysis_result = get_image_analysis_result(result, source_image)
  ocr_result["analysis_result"] = analysis_result
  inserted_id = insert_analysis(ocr_result["analysis_result"])
  insert_aggregate_result(inserted_id, ocr_result["aggregate_result"])
  return ocr_result

def get_ocr_result(result):
  string_list = []

  if result.reason != sdk.ImageAnalysisResultReason.ANALYZED:
    return sdk.ImageAnalysisErrorDetails.from_result(result)
  else:
    if result.text is not None:
      for line in result.text.lines:
        for word in line.words:
          string_list.append(word.content)

  number_list = convert_to_decimal_list(string_list)

  aggregate_result = aggregate_operations(number_list)

  return {
    "aggregate_result": aggregate_result,
    "numbers_read": string_list
  }

def get_image_analysis_result(result, source_image):
  
  analysis_result = { }
  string_list = []

  if result.reason != sdk.ImageAnalysisResultReason.ANALYZED:
    return sdk.ImageAnalysisErrorDetails.from_result(result)
  else:
    if result.caption is not None:
        analysis_result["caption"] = { 
                                      "content": result.caption.content,
                                      "confidence": result.caption.confidence
                                      }
        
        analysis_result["text"] = {
                                      "lines": []
                                  }

    if result.text is not None:
      for line in result.text.lines:
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
          string_list.append(word.content)
          line_result["words"].append(word_result)

        document_id = os.path.basename(source_image).rsplit('.', 1)[0]
        base_file_name, ext = source_image.split('.')
        result_file = '{}.{}'.format(base_file_name, 'json')

        analysis_result["file_name"] = result_file
        analysis_result["text"]["lines"].append(line_result)
        analysis_result["id"] = document_id
        analysis_result["partitionKey"] = "Partition1"

      return analysis_result

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
