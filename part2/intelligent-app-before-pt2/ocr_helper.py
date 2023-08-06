import os
from statistics import median
from decimal import Decimal
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

  string_list = []

  if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:
    if result.text is not None:
      for line in result.text.lines:
        points_string = ("{" +
        ", ".join([str(int(point)) for point in line.bounding_polygon]) + 
        "}")
        for word in line.words:
          points_string = ("{" +
                   ", ".join([str(int(p)) for p in word.bounding_polygon]) +
                   "}")
          string_list.append(word.content)

  else:
    error_details = sdk.ImageAnalysisErrorDetails.from_result(result)

  number_list = convert_to_decimal_list(string_list)

  return aggregate_operations(number_list)

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
