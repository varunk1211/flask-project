from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import numpy as np
import base64

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow cross-origin requests

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("video_frame")
def handle_video(data):
    try:
        # Decode base64 image
        image_data = base64.b64decode(data.split(",")[1])
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Apply grayscale filter
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Encode processed frame back to base64
        _, buffer = cv2.imencode(".jpg", gray_frame)
        processed_image = base64.b64encode(buffer).decode("utf-8")

        # Send processed frame back to client
        emit("processed_frame", f"data:image/jpeg;base64,{processed_image}")

    except Exception as e:
        print(f"Error processing frame: {e}")

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
