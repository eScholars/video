import secrets, threading, requests
from flask import Flask, jsonify, request, Response
import moviepy.editor as editor


app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({ "d": "Hello, World!" })

@app.route("/process", methods=['post'])
def process():
    # video   -  String, video file name including extension
    # length  -  Integer, video file length
    
    # key - random 16 chars that will be used to respond once processed
    # status - integer: 0 = ignoring, 1 = queued, 2 = processing now

    data = request.get_json(silent=True)

    if "file" not in data or "length" not in data or "callback" not in data or "id" not in data:
        return jsonify({ "key": '', "status": 0 }), 400, {'Content-Type': "application/json"}


    key = secrets.token_hex(18)

    video = {"video": data['video'], "length": data["length"], "callback": data['callback'], "id": data["id"], "key": key}
    thread = threading.Thread(target=proccess_video, kwargs=video)
    thread.start()
    return jsonify({ "key": key, "status": 1 })


def proccess_video(**data):
    id = data.get("id")
    clip = editor.VideoFileClip(data.get("video"))
    clip.write_videofile(f"{id}.mp4")

    r = requests.post(data.get("callback"), json={"status": 2}, headers={ 'Authorization': 'Bearer {}'.format(data.get("key")) })
    print(f"Recieved {r.status_code}")

if __name__ == "__main__":
    app.run() 