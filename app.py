from flask import *
from mongoengine import *

connect("c4e6db", host="ds053126.mlab.com", port=53126, username="admin", password="admin")

class Upload_info(Document):
    img_upload = StringField()
    des = StringField()

class Pets(Document):
    name = StringField()
    img_ava = StringField()
    rank = IntField()
    like_count = IntField()
    upload_info = EmbeddedDocumentField("Upload_info")

class Users(Document):
    username = StringField()
    password = StringField()
    pet = EmbeddedDocumentField("Pets")


app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template("homepage.html", users=Users.objects)

@app.route('/profile')
def get_profile():
    return "Test"

if __name__ == '__main__':
    app.run()
