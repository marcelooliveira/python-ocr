import os

from flask import Flask, request
from flask_restful import Resource, Api
from quickstart import process_ocr
import json
from werkzeug.utils import secure_filename

app = Flask(__name__,
            static_url_path='', 
            static_folder='static/files')

api = Api(app)

UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = {'png', 'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

api = Api(app)

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
            upload_folder = "static/files"
            local_file_path = os.path.join(upload_folder, filename)
            file.save(local_file_path)
        
            try:
                aggregates = process_ocr(local_file_path)
                return json.dumps(aggregates, default=str) 
            except ValueError:
                return -777

api.add_resource(UploadHandler, "/")

if __name__ == '__main__':
    app.run(debug=True)
    
