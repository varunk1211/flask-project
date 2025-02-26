from flask import Flask, Response, render_template_string
import cv2
import threading

app = Flask(__name__)

# Initialize the video capture
cap = cv2.VideoCapture(0)

# A flag to control the video stream
video_streaming = False

# Function to generate video frames
def generate_frames():
    while video_streaming:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame in the correct format for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# Start the video stream
@app.route('/start')
def start_video():
    global video_streaming
    video_streaming = True
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
        # Return the response with the generated frames
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return "Video not started."

@app.route('/')
def index():
    # Return the HTML page with buttons to start and stop the video
    return render_template_string('''
        <html>
            <head>
                <script>
                    function startVideo() {
                        fetch('/start').then(response => response.text()).then(data => {
                            document.getElementById("status").innerText = "Video is running...";
                            document.getElementById("videoStream").src = "/video";
                        });
                    }

                    function stopVideo() {
                        fetch('/stop').then(response => response.text()).then(data => {
                            document.getElementById("status").innerText = "Video stopped.";
                            document.getElementById("videoStream").src = "";
                        });
                    }
                </script>
            </head>
            <body>
                <h1>OpenCV Video Stream</h1>
                <p id="status">Video is not running.</p>
                <button onclick="startVideo()">Start Video</button>
                <button onclick="stopVideo()">Stop Video</button>
                <br><br>
                <img id="videoStream" width="640" height="480" />
            </body>
        </html>
    ''')

if __name__ == '__main__':
    app.run(debug=True)
