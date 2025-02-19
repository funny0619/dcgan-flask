from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import requests
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from flask_cors import CORS
import os
import uuid
app = Flask(__name__)

storage_connection_string = 'DefaultEndpointsProtocol=https;AccountName=dcganstorage;AccountKey=b5svPLofeg19An4IAWspkSdrIpdi8cOhMsFHYElhMpHyoRTHZgV1kOX+Esy9UFcVKRx1fzBWYqTt+ASt5ou3Jg==;EndpointSuffix=core.windows.net'
blob_service_client = BlobServiceClient.from_connection_string(
    storage_connection_string)
container_name = 'dcganwav'
container_client = blob_service_client.get_container_client(container_name)
cwd = os.getcwd()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/waiting/<process_id>")
def waiting(process_id):
    return render_template("waiting.html", process_id=process_id)


@app.route('/generated')
def generated():
    process_id = request.args.get('process_id')
    return render_template("audio.html", process_id=process_id)


@app.route('/error')
def error():
    code = int(request.args.get('code', 0))
    if 500 <= code < 600:
        error_message = "Internal Server Error"
    elif 400 <= code < 500:
        error_message = "Bad Request"
    elif code == 0:
        error_message = "Connection Error with Server Try again later"
    return render_template("error.html", error_code=code, error_message=error_message)


@app.route('/generate', methods=['POST'])
def generate():
    instrument = request.form.get('instrument', 'drum')

    process_id = str(uuid.uuid4())

    json_payload = {
        'instrument': instrument,
        'process_id': process_id,
    }

    res = requests.post('http://13.64.211.233/generate/', json=json_payload)
    if res.status_code != 200:
        code = res.status_code
        return redirect(url_for('error', code=code))
    else:

        return redirect(url_for('waiting', process_id=process_id))


@app.route('/image/<process_id>')
def serve_image(process_id):
    filename = f"{process_id}/bmp_file.bmp"
    print(filename)
    try:
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=filename)
        download_stream = blob_client.download_blob()
    except ResourceNotFoundError:
        return redirect(url_for('error', code=0))

    def generate():
        for chunk in download_stream.chunks():
            yield chunk

    return Response(
        generate(),
        mimetype='image/bmp',
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


@app.route('/audio/<process_id>')
def serve_audio(process_id):
    filename = f"{process_id}/wav_file.wav"
    print(filename)
    try:
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=filename)
        download_stream = blob_client.download_blob()
    except ResourceNotFoundError:
        return redirect(url_for('error', code=0))

    def generate():
        for chunk in download_stream.chunks():
            yield chunk

    return Response(
        generate(),
        mimetype='audio/mpeg',
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


if __name__ == "__main__":
    app.run(debug=True)
