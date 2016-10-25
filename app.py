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

@app.route('/', methods=["GET", "POST"])
def home_page():
    if request.method == "GET":
        return render_template("homepage.html", users=Users.objects)
    elif request.method == "POST":
        username = request.form["username"]
        votes = request.form["votes"]
        Users.objects(username=username).update_one(set__pet__like_count=votes)
        return jsonify({"votes": votes, "username": username})

@app.route('/profile')
def get_profile():
    return "Test"

if __name__ == '__main__':
    app.run()
