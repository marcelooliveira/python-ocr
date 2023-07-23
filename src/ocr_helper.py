"""Module providing functions for processing images."""
import os
from statistics import median
from decimal import Decimal
import azure.ai.vision as sdk

def process_ocr(source_image):
    """Process OCR from an image."""
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
            print(f"  '{result.caption.content}', Confidence {result.caption.confidence:.4f}")

        if result.text is not None:
            print("Text:")
            for line in result.text.lines:
                points_string = ("{" +
                ", ".join([str(int(point)) for point in line.bounding_polygon]) + 
                "}")
                print(f"  Line: '{line.content}', Bounding polygon {points_string}")
                for word in line.words:
                    points_string = ("{" +
                                     ", ".join([str(int(p)) for p in word.bounding_polygon]) +
                                     "}")
                    print(f"    Word: '{word.content}', " \
                          "Bounding polygon {points_string}, Confidence {word.confidence:.4f}")
                    string_list.append(word.content)

    else:
        error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
        print("Analysis failed.")
        print(f"  Error reason: {error_details.reason}")
        print(f"  Error code: {error_details.error_code}")
        print(f"  Error message: {error_details.message}")

    number_list = convert_to_decimal_list(string_list)

    return aggregate_operations(number_list)

def convert_to_decimal_list(string_list):
    """Returns a list of decimal numbers from a list of strings."""
    return list(map(Decimal, string_list))

def aggregate_operations(numbers):
    """Return aggregate operations from a list of numbers."""
    result = {
        'sum': sum(numbers),
        'average': sum(numbers) / len(numbers),
        'median': median(numbers),
        'min': min(numbers),
        'max': max(numbers)
    }
    return result
