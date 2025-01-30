from flask import Flask, send_from_directory, render_template, send_file, Response
from flask_cors import CORS


app = Flask(__name__)
cors = CORS(app)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin']='*'
    response.headers['Access-Control-Allow-Origin']='*'
    response.headers['Vary']='Origin'
    return response


@app.route('/videojs/<path:path>')
def send_videojs(path):
    return send_from_directory('videojs',path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video/video.mpd')
def send_mpd():
    return send_file('video/video.mpd', mimetype='application/dash+xml')

@app.route('/video/<path:filename>', methods=['GET'], strict_slashes=False)
def send_chunk(filename):
    return send_from_directory('video', filename) 

@app.route('/video/')
def list_video(filename):
    file_list = os.listdir(video)
    return '<br>'.join(file.list) 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
