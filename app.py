from flask import *
from mongoengine import *
import os
from werkzeug.utils import secure_filename

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(APP_ROOT, "static")
UPLOAD_FOLDER = os.path.join(APP_ROOT, "static", "uploads")

connect("c4e6db", host="ds053126.mlab.com", port=53126, username="admin", password="admin")

class Upload(Document):
    img_upload = StringField()
    caption = StringField()
    liked_users = ListField()

class Pet(Document):
    name = StringField()
    img_ava = StringField()
    des = StringField()
    like_count = IntField()
    liked_users = ListField()
    uploads = EmbeddedDocumentListField("Upload")

class Users(Document):
    username = StringField()
    password = StringField()
    rank = IntField()
    pet = EmbeddedDocumentField("Pet")

app = Flask(__name__, static_folder=STATIC_FOLDER)
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
                found_user = None
                for user in Users.objects:
                    if user.username == username_signup and user.password == password_signup:
                        found_user = user
                        break
                if found_user:
                    session["user"] = user.username
                    return redirect(url_for("home"))

@app.route('/home', methods=['GET', 'POST'])
def home():
    if "user" in session:
        logged_in_user_name = session["user"]
        logged_in_user = Users.objects(username=logged_in_user_name).first()
        if request.method == "GET":
            rank_list = []
            for user in Users.objects:
                if user.pet is not None:
                    rank_list.append((user.pet.like_count, user.username))
                    rank_list.sort(reverse=True)
            for user in Users.objects:
                if user.pet is not None:
                    rank = rank_list.index((user.pet.like_count, user.username)) + 1
                    Users.objects(username=user.username).update_one(set__rank=rank)
            return render_template("homepageloggedin.html", users=Users.objects,
                                                            logged_in_user=logged_in_user,
                                                            rank=rank_list)
        elif request.method == "POST":
            username = request.form["username"]
            votes = request.form["votes"]
            if logged_in_user.username not in Users.objects.get(username=username).pet["liked_users"]:
                votes = int(votes) + 1
                Users.objects(username=username).update_one(set__pet__like_count=votes,
                                                            add_to_set__pet__liked_users=session["user"], )
        return jsonify({"votes": votes})
    else:
        return redirect(url_for("home_page"))

# <s href=profile/{{user.username}}

# <a href=url_for("get_profile",username={{user.username}}) />

@app.route('/profile/<username>', methods=["GET", "POST"])
def get_profile(username):
    if "user" not in session:
        return redirect(url_for("home_page"))
    else:
        logged_in_user_name = session["user"]
        logged_in_user = Users.objects(username=logged_in_user_name).first()
        profile_user = Users.objects(username=username).first()
        if request.method == "GET":
            rank_list = []
            for user in Users.objects:
                if user.pet is not None:
                    rank_list.append((user.pet.like_count, user.username))
                    rank_list.sort(reverse=True)
            for user in Users.objects:
                if user.pet is not None:
                    rank = rank_list.index((user.pet.like_count, user.username)) + 1
                    Users.objects(username=user.username).update_one(set__rank=rank)
            return render_template("profile.html", user=profile_user, logged_in_user=logged_in_user)
        elif request.method == "POST":
            if "update_profile" in request.form:
                name = request.form["name"]
                des = request.form["des"]
                img_ava = request.files["img_ava"]
                img_name = secure_filename(img_ava.filename)
                img_path = os.path.join(app.config["UPLOAD_FOLDER"], img_name)
                img_ava.save(img_path)
                pet = Pet(name=name, img_ava=img_name, des=des, like_count=0)
                Users.objects(username=username).update_one(set__pet=pet)
                return redirect(url_for("get_profile", username=logged_in_user.username))
            elif "upload" in request.form:
                img_upload = request.files["img_upload"]
                caption = request.form["caption"]
                img_name = secure_filename(img_upload.filename)
                img_path = os.path.join(app.config["UPLOAD_FOLDER"], img_name)
                img_upload.save(img_path)
                upload = Upload(img_upload=img_name, caption=caption)
                Users.objects(username=username).update_one(add_to_set__pet__uploads=upload)
                return redirect(url_for("get_profile", username=username))
            else:
                votes = request.form["votes"]
                found_document = Users.objects.get(username=username)
                if logged_in_user.username not in found_document.pet["liked_users"]:
                    votes = int(votes) + 1
                    Users.objects(username=username).update_one(set__pet__like_count=votes,
                                                                add_to_set__pet__liked_users=logged_in_user.username, )
                return jsonify({"votes": votes})

@app.route('/signout')
def do_signout():
    session.pop("user", None)
    return redirect(url_for("home_page"))

if __name__ == '__main__':
    app.run(port=5005)
