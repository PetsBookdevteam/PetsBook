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

@app.route('/signup', methods=['GET', 'POST'])
def do_signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = Users(username=username, password=password)
        user.save()
        return redirect(url_for("do_signin"))

@app.route('/signin')
def do_signin():
    return 'Signed In'
if __name__ == '__main__':
    app.run()
