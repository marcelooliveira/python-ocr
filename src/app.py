from flask import Flask
from flask_restful import Resource, Api
from quickstart import process_ocr
from json import dumps

app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        source_image = "https://learn.microsoft.com/azure/cognitive-services/computer-vision/media/quickstarts/presentation.png"
        report = process_ocr(source_image)
        return report

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)