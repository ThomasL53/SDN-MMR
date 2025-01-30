from flask import Flask, send_from_directory, render_template, send_file, Response
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

@app.route('/videojs/<path:path>')
def send_videojs(path):
    return send_from_directory('videojs',path)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
