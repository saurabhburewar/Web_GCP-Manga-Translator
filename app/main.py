import json
import time
from flask import Flask, request
from google.cloud import storage

st_client1 = storage.Client()


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def get_img():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files.get('file')

            in_bucket = "sde-mangas"
            bucket1 = st_client1.get_bucket(in_bucket)
            blob1 = bucket1.blob(file.filename)
            blob1.content_type = "image/jpeg"

            print("Uploading to {} in {}".format(file, in_bucket))
            blob1.upload_from_file(file)
            print("File uploaded")

            print("Waiting for translations...")
            time.sleep(5)

            out_bucket = "sde-texts"
            bucket2 = st_client1.get_bucket(out_bucket)
            blob2 = bucket2.get_blob("{}_en.txt".format(file.filename))

            resp = blob2.download_as_string()
            resp = resp.decode('utf-8')

            return json.dumps(resp)

    return '''
    <!doctype html>
    <title>Manga text translations</title>
    <head>
    <style>
    * {margin:0; padding:0;}
    body {background:#fff; width:100%; height:100vh;}
    h1 {width:100%; height:20%; display:flex; justify-content:center; align-items:flex-end; color:#000;}
    div {width:100%; height:15%; display:flex; justify-content:center; align-items:center;}
    </style>
    </head>
    <body>
    <h1>Upload Image</h1>
    <div>
    <form method=post enctype=multipart/form-data>
    <input type=file name=file>
    <input class="submit_input" type=submit value=Upload>
    </form>
    </div>
    </body>
    '''


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
