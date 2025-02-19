from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, session
import requests
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import os
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
storage_connection_string = 'DefaultEndpointsProtocol=https;AccountName=dcganstorage;AccountKey=b5svPLofeg19An4IAWspkSdrIpdi8cOhMsFHYElhMpHyoRTHZgV1kOX+Esy9UFcVKRx1fzBWYqTt+ASt5ou3Jg==;EndpointSuffix=core.windows.net'
blob_service_client = BlobServiceClient.from_connection_string(
    storage_connection_string)
container_name = 'dcganwav'
container_client = blob_service_client.get_container_client(container_name)
cwd = os.getcwd()

process_store = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/waiting")
def waiting():
    return render_template("waiting.html")


@app.route('/generated')
def generated():
    filename = request.args.get('wav_file')
    wav_file = request.args.get('wav_file')
    bmp_file = request.args.get('bmp_file')
    process_store['ready'] = False
    process_store['wav_file'] = None
    process_store['bmp_file'] = None
    process_store.pop("ready", None)
    chosen_instrument = session.get('chosen_instrument', 'drum')
    return render_template("audio.html", wav_file=wav_file, bmp_file=bmp_file, instrument=chosen_instrument)


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
    session['chosen_instrument'] = instrument

    sesssion_cookie = request.cookies.get(
        app.config.get("SESSION_COOKIE_NAME", "session"))
    json_payload = {
        'instrument': instrument,
        'token': sesssion_cookie
    }

    sesssion_cookie = request.cookies.get(
        app.config.get("SESSION_COOKIE_NAME", "session"))

    res = requests.post('http://23.100.34.121/generate/', json=json_payload)
    if res.status_code != 200:
        code = res.status_code
        return redirect(url_for('error', code=code))
    else:
        return redirect(url_for('waiting'))


@app.route('/api/finished', methods=['POST'])
def api_finished():
    data = request.get_json()
    if not data or 'bmp_file' not in data or 'wav_file' not in data or 'token' not in data:
        return jsonify({"error": "Invalid payload"}), 400

    received_token = data['token']
    session_token = request.cookies.get(
        app.config.get("SESSION_COOKIE_NAME", "session"))
    if received_token != session_token:
        return jsonify({"error": "Invalid Token"}), 404

    wav_file = data['wav_file'].split('/')[-1]
    bmp_file = data['bmp_file'].split('/')[-1]
    process_store['ready'] = True
    process_store['wav_file'] = wav_file
    process_store['bmp_file'] = bmp_file
    return jsonify({"status": "file ready", "wav_file": wav_file, "bmp_file": bmp_file})


@app.route('/status')
def status():
    ready = process_store.get('ready', False)
    if ready:
        print(process_store)
        return jsonify({'ready': ready, 'wav_file': process_store['wav_file'], 'bmp_file': process_store['bmp_file']})
    else:
        return jsonify({'ready': ready})


@app.route('/audio/<filename>')
def serve_image(filename):
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


@app.route('/audio/<filename>')
def serve_audio(filename):
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
