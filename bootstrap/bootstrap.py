from flask import *
from mongoengine import *
import os
from werkzeug.utils import secure_filename
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'uploads')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


class Inform(Document):
    title = StringField()
    description = StringField()
    image = StringField()

db_name = 'nguyenhuumanh'
host = 'ds053206.mlab.com'
port = 53206
user_name = 'admin'
password = 'admin'
connect(db_name,
        host=host,
        port=port,
        username=user_name,
        password=password)


@app.route('/blue')
def testing():
    return "Hihi"

@app.route('/')
@app.route('/upload', methods=['GET', 'POST'])
def upload_info():
    if request.method == 'GET':
        return render_template('index.html', pets=Inform.objects)
    elif request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        uploaded_image = request.files['image_file']
        filename = secure_filename(uploaded_image.filename)
        check = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(check):
            return redirect(url_for('upload_info'))
        else:
            save_file_name = check
            uploaded_image.save(save_file_name)
            c = Inform(title=title, description=desc, image=filename)
            c.save()
            return redirect(url_for('upload_info'))

if __name__ == '__main__':
    app.run()
