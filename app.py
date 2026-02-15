import os
import subprocess
from flask import Flask, render_template, request

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CLIPS_FOLDER = "clips"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLIPS_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    video = request.files['video']
    video_path = os.path.join(UPLOAD_FOLDER, video.filename)
    video.save(video_path)

    # Get video duration
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries',
         'format=duration', '-of',
         'default=noprint_wrappers=1:nokey=1', video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    
    duration = float(result.stdout)
    clip_length = 60  # 60 seconds per short
    start = 0
    clip_number = 1

    while start < duration:
        output_path = os.path.join(CLIPS_FOLDER, f"short_{clip_number}.mp4")

        subprocess.run([
            'ffmpeg',
            '-i', video_path,
            '-ss', str(start),
            '-t', str(clip_length),
            '-vf', 'crop=ih*9/16:ih',  # convert to vertical
            '-c:a', 'copy',
            output_path
        ])

        start += clip_length
        clip_number += 1

    return "Shorts created successfully! Check clips folder."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
