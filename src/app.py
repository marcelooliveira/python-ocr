from flask import Flask
from flask_restful import Resource, Api
from quickstart import process_ocr
from json import dumps

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        # source_image = "https://learn.microsoft.com/azure/cognitive-services/computer-vision/media/quickstarts/presentation.png"
        source_image = "https://github.com/marcelooliveira/python-ocr/blob/main/src/sample1.jpg"
        sum = process_ocr(source_image)
        return sum

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)