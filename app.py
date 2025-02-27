import eventlet
eventlet.monkey_patch()  # Monkey-patch for asynchronous I/O
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import numpy as np
import base64
from eventlet import wsgi

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")  # Use eventlet for async

@app.route("/")
def index():
    return render_template("index.html")

def apply_filter(frame, filter_type):
    if filter_type == "grayscale":
        # Convert to grayscale
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
    elif filter_type == "sepia":
        # Apply sepia filter
        kernel = np.array([[0.393, 0.769, 0.189], 
                           [0.349, 0.686, 0.168], 
                           [0.272, 0.534, 0.131]])
        return cv2.transform(frame, kernel)
        
    elif filter_type == "invert":
        # Invert colors
        return cv2.bitwise_not(frame)
        
    return frame  # No filter

@socketio.on("video_frame")
def handle_video(data):
    try:
        # Decode base64 image
        image_data = base64.b64decode(data['imageData'].split(",")[1])
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Apply the selected filter
        filter_type = data['filter']
        processed_frame = apply_filter(frame, filter_type)

        # Encode processed frame back to base64
        if len(processed_frame.shape) == 2:  # Grayscale image (2D)
            processed_frame = cv2.cvtColor(processed_frame, cv2.COLOR_GRAY2BGR)
            
        _, buffer = cv2.imencode(".jpg", processed_frame)
        processed_image = base64.b64encode(buffer).decode("utf-8")

        # Send processed frame back to client
        emit("processed_frame", f"data:image/jpeg;base64,{processed_image}")

    except Exception as e:
        print(f"Error processing frame: {e}")

if __name__ == "__main__":
   wsgi.server(eventlet.listen(('0.0.0.0', 5001)), app)  # Specify host and port here
