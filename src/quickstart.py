import os
import azure.ai.vision as sdk
from statistics import median
from decimal import Decimal

def process_ocr(source_image):
    print(f"Processing image: {source_image}")

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
        if result.caption is not None:
            print("Caption:")
            print("  '{}', Confidence {:.4f}".format(result.caption.content, result.caption.confidence))

        if result.text is not None:
            print("Text:")
            for line in result.text.lines:
                points_string = "{" + ", ".join([str(int(point)) for point in line.bounding_polygon]) + "}"
                print("  Line: '{}', Bounding polygon {}".format(line.content, points_string))
                for word in line.words:
                    points_string = "{" + ", ".join([str(int(point)) for point in word.bounding_polygon]) + "}"
                    print("    Word: '{}', Bounding polygon {}, Confidence {:.4f}".format(word.content, points_string, word.confidence))
                    string_list.append(word.content)

    else:
        error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
        print("Analysis failed.")
        print("  Error reason: {}".format(error_details.reason))
        print("  Error code: {}".format(error_details.error_code))
        print("  Error message: {}".format(error_details.message))

    convert_to_decimal_list = lambda string_list: list(map(Decimal, string_list))
    
    number_list = convert_to_decimal_list(string_list)
 
    return aggregate_operations(number_list)

def aggregate_operations(numbers):
    result = {
        'sum': sum(numbers),
        'average': sum(numbers) / len(numbers),
        'median': median(numbers),
        'min': min(numbers),
        'max': max(numbers)
    }
    return result