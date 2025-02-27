from flask import Flask, Response, render_template
import cv2
import threading

app = Flask(__name__)

# Global variables for video streaming
cap = None
video_streaming = False
frame_lock = threading.Lock()
frame = None

# Background thread function to capture video frames
def capture_frames():
    global cap, frame, video_streaming
    cap = cv2.VideoCapture(0)  # Open webcam
    while video_streaming:
        success, temp_frame = cap.read()
        if not success:
            break
        with frame_lock:
            frame = temp_frame

    cap.release()  # Release camera when stopping

# Function to generate video frames
def generate_frames():
    global frame
    while video_streaming:
        with frame_lock:
            if frame is None:
                continue
            success, buffer = cv2.imencode('.jpg', frame)
        if success:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n\r\n')

# Start the video stream
@app.route('/start')
def start_video():
    global video_streaming
    if not video_streaming:
        video_streaming = True
        threading.Thread(target=capture_frames, daemon=True).start()  # Run capture in background
    return "Video started"

# Stop the video stream
@app.route('/stop')
def stop_video():
    global video_streaming
    video_streaming = False
    return "Video stopped"

@app.route('/video')
def video():
    if video_streaming:
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Video not started."

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
