from flask import Flask, render_template, request, url_for, redirect
from werkzeug.utils import secure_filename
from os.path import isfile, join
import os
import main

UPLOAD_FOLDER = 'temp_img'

# list_file = [join('static/images/aristino.com', f) for f in os.listdir('static/images/aristino.com') if isfile(join('static/images/aristino.com', f))]
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
@app.route('/index')

def index():
    return render_template('csdldpt.html')

@app.route('/submit', methods=['GET', 'POST'])

def submit():
    if request.method == 'POST' and request.files['img1']:
        type = request.form['type']
        gender = request.form['gioi_tinh']
        img = request.files['img1']
        filename = secure_filename(img.filename)
        filename = 'query/{}'.format(filename)
        img.save(os.path.join('static',filename))
        list_file, id = main.executeQuery(type,'static/{}'.format(filename))
        results = main.compare('static/{}'.format(filename), 'Correlation', list_file)
        return render_template('Results.html', url=url_for('static', filename=filename), gender=gender, type=type,
                               results=results, id=id)
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug= True)
