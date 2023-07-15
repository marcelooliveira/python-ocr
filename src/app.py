import os

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from quickstart import process_ocr
import json
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__,
            static_url_path='', 
            static_folder='static/files')

api = Api(app)

UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = {'png', 'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

api = Api(app)

# class HelloWorld(Resource):
#     def get(self):
#         # source_image = "https://learn.microsoft.com/azure/cognitive-services/computer-vision/media/quickstarts/presentation.png"
#         source_image = "https://raw.githubusercontent.com/marcelooliveira/python-ocr/main/src/sample1.png"
#         sum = process_ocr(source_image)
#         return sum

class UploadHandler(Resource):

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def post(self):
        # Get Text type fields
        form = request.form.to_dict()
        print(form)

        if 'file' not in request.files:
            return json.dumps({ "success": False, "error": "No file part"})
        
        file = request.files.get("file")
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # upload_folder = app.config['UPLOAD_FOLDER']
            upload_folder = "static/files"
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
    
            data = file.read()
            f = open(file_path, "rb")
            file_content = f.read()
            data = base64.b64encode(file_content).decode()  
            file_path = request.base_url + "static/files/" + file.filename
            
            # return json.dumps({ "success": True, "fileSize": len(data) })
            # return jsonify({
            #     'msg': 'success', 
            #     # 'size': [img.width, img.height], 
            #     # 'format': img.format,
            #     'filename': file.filename,
            #     'img': len(data),
            #     'base_url': request.base_url,
            #     'file_path': file_path
            # })
        
            sum = process_ocr(file_path)
            return sum 

api.add_resource(UploadHandler, "/")

if __name__ == '__main__':
    app.run(debug=True)
