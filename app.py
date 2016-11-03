from flask import *
from mongoengine import *
import os
from werkzeug.utils import secure_filename

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, "static", "uploads")

connect("c4e6db", host="ds053126.mlab.com", port=53126, username="admin", password="admin")

class Upload(Document):
    img_upload = ListField()
    caption = ListField()
    liked_users = ListField()

class Pet(Document):
    name = StringField()
    img_ava = StringField()
    des = StringField()
    rank = IntField()
    like_count = IntField()
    liked_users = ListField()
    upload = EmbeddedDocumentField("Upload")

class Users(Document):
    username = StringField()
    password = StringField()
    pet = EmbeddedDocumentField("Pet")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "PetsBookDevTe@m"

@app.route('/', methods=["GET", "POST"])
def home_page():
    if "user" in session:
        return redirect(url_for("home"))
    else:
        if request.method == "GET":
            return render_template("homepage.html", users=Users.objects)
        elif request.method == "POST":
            if 'signin' in request.form:
                username_signin = request.form["username_signin"]
                password_signin = request.form["password_signin"]
                found_user = None
                for user in Users.objects:
                    if user.username == username_signin and user.password == password_signin:
                        found_user = user
                        break
                if found_user:
                    session["user"] = user.username
                    return redirect(url_for("home"))
                else:
                    alert_signin = "User not found. Please try again!"
                    return render_template("signin.html", alert_signin=alert_signin)
            elif 'signup' in request.form:
                username_signup = request.form["username_signup"]
                password_signup = request.form["password_signup"]
                for user in Users.objects:
                    if user.username == username_signup:
                        alert_signup = "This username has already been taken!"
                        return render_template("homepage.html", alert_signup=alert_signup)
                user = Users(username=username_signup, password=password_signup)
                user.save()
                return render_template("signin.html")

@app.route('/home', methods=['GET', 'POST'])
def home():
    if "user" in session:
        if request.method == "GET":
            liked_user = session["user"]
            rank_list = []
            for user in Users.objects:
                if user.pet is not None:
                    rank_list.append((user.pet.like_count, user.username))
                    rank_list.sort(reverse=True)
            return render_template("homepageloggedin.html", users=Users.objects, liked_user=liked_user, rank=rank_list)
        elif request.method == "POST":
            username = request.form["username"]
            votes = request.form["votes"]
            found_document = Users.objects.get(username=username)
            if session["user"] not in found_document.pet.liked_users:
                votes = int(votes) + 1
                Users.objects(username=username).update_one(set__pet__like_count=votes,
                                                            add_to_set__pet__liked_users=session["user"], )
        return jsonify({"votes": votes})
    else:
        return redirect(url_for("home_page"))

@app.route('/profile', methods=["GET", "POST"])
def get_profile():
    if "user" not in session:
        return redirect(url_for("home_page"))
    username = session["user"]
    user = Users.objects(username=username).first()
    if request.method == "GET":
        return render_template("profile.html", user=user)
    elif request.method == "POST":
        img_upload = request.files["img_upload"]
        caption = request.form["caption"]
        img_name = secure_filename(img_upload.filename)
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], img_name)
        img_upload.save(img_path)
        upload = Upload(img_upload=img_upload, caption=caption)
        upload.save()
        Users.objects(username=username).update_one(set__pet__upload=upload)
        return "Uploaded"

@app.route('/signout')
def do_signout():
    session.pop("user", None)
    return redirect(url_for("home_page"))

if __name__ == '__main__':
    app.run(port=5005)
