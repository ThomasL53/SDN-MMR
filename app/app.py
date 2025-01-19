from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h1>Partage de vidéo avec Flask</h1>
    <video width="320" height="240" controls>
      <source src="/" type="video/mp4">
      Your browser does not support the video tag.
    </video>
    '''

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def default():
    return send_file('video.mp4', mimetype='video/mp4')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
