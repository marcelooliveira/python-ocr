import os
import json

from flask import Flask, request
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename

app = Flask(__name__,
      static_url_path='',
      static_folder='static/files')

api = Api(app)

app = Flask(__name__) 
app.config['UPLOAD_FOLDER'] = 'files'

api = Api(app)

class UploadHandler(Resource):

  def allowed_file(self, filename):
    return '.' in filename and \
      filename.rsplit('.', 1)[1].lower() in {'png'}

  def post(self):
    form = request.form.to_dict()

    if 'file' not in request.files:
      return json.dumps({ "success": False, "error": "No file part"})

    file = request.files.get("file")
    if file and self.allowed_file(file.filename):
      filename = secure_filename(file.filename)
      upload_folder = "static/files"
      if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
      local_file_path = os.path.join(upload_folder, filename)
      file.save(local_file_path)

      return f"File {filename} uploaded successfully to folder: {upload_folder}"

api.add_resource(UploadHandler, "/")

if __name__ == '__main__':
  app.run(debug=True)
