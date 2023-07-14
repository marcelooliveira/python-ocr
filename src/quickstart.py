import os
import azure.ai.vision as sdk

def process_ocr(source_image):
    service_options = sdk.VisionServiceOptions(os.environ["VISION_ENDPOINT"],
                                           os.environ["VISION_KEY"])

    vision_source = sdk.VisionSource(url=source_image)

    analysis_options = sdk.ImageAnalysisOptions()

    analysis_options.features = (
        sdk.ImageAnalysisFeature.CAPTION |
        sdk.ImageAnalysisFeature.TEXT
    )

    analysis_options.language = "en"

    analysis_options.gender_neutral_caption = True

    image_analyzer = sdk.ImageAnalyzer(service_options, vision_source, analysis_options)

    result = image_analyzer.analyze()

    report = ""

    if result.reason == sdk.ImageAnalysisResultReason.ANALYZED:
        if result.caption is not None:
            report = report + "\r\n Caption:"
            report = report + "\r\n   '{}', Confidence {:.4f}".format(result.caption.content, result.caption.confidence)

        if result.text is not None:
            report = report + "\r\n Text:"
            for line in result.text.lines:
                points_string = "{" + ", ".join([str(int(point)) for point in line.bounding_polygon]) + "}"
                report = report + "\r\n   Line: '{}', Bounding polygon {}".format(line.content, points_string)
                for word in line.words:
                    points_string = "{" + ", ".join([str(int(point)) for point in word.bounding_polygon]) + "}"
                    report = report + "\r\n     Word: '{}', Bounding polygon {}, Confidence {:.4f}".format(word.content, points_string, word.confidence)

    else:
        error_details = sdk.ImageAnalysisErrorDetails.from_result(result)
        report = report + "\r\n Analysis failed."
        report = report + "\r\n   Error reason: {}".format(error_details.reason)
        report = report + "\r\n   Error code: {}".format(error_details.error_code)
        report = report + "\r\n   Error message: {}".format(error_details.message)

    return report
