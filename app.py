from flask import *
from mongoengine import *

connect("c4e6db", host="ds053126.mlab.com", port=53126, username="admin", password="admin")

class Upload_info(Document):
    img_upload = StringField()
    des = StringField()

class Pet(Document):
    name = StringField()
    img_ava = StringField()
    rank = IntField()
    like_count = IntField()
    liked_users = ListField()
    upload_info = EmbeddedDocumentField("Upload_info")

class Users(Document):
    username = StringField()
    password = StringField()
    pet = EmbeddedDocumentField("Pet")

app = Flask(__name__)

app.config["SECRET_KEY"] = "PetsBookDevTe@m"

@app.route('/', methods=["GET", "POST"])
def home_page():
    return render_template("homepage.html", users=Users.objects)

@app.route('/signup', methods=['GET', 'POST'])
def do_signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        for user in Users.objects:
            if user.username == username:
                alert = "Your username has already been taken. Try another!"
                return render_template("signup.html", alert=alert)
        user = Users(username=username, password=password)
        user.save()
        return redirect(url_for("do_signin"))

@app.route('/signin', methods=['GET', 'POST'])
def do_signin():
    if request.method == "GET":
        return render_template("signin.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        found_user = False
        for user in Users.objects:
            if user.username == username and user.password == password:
                found_user = True
                break
        if found_user:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return "User not found"

@app.route('/home', methods=['GET', 'POST'])
def home():
    if "user" in session and session["user"]:
        if request.method == "GET":
            liked_user = session["user"]
            return render_template("homepageloggedin.html", users=Users.objects, liked_user=liked_user)
        elif request.method == "POST":
            username = request.form["username"]
            votes = request.form["votes"]
            found_document = Users.objects.get(username=username)
            if session["user"] not in found_document.pet["liked_users"]:
                votes = int(votes) + 1
                Users.objects(username=username).update_one(set__pet__like_count=votes,
                                                            add_to_set__pet__liked_users=session["user"], )
        return jsonify({"votes": votes})
    else:
        return redirect(url_for("do_signup"))
@app.route('/signout')
def do_signout():
    session.pop("user", None)
    return redirect(url_for("home_page"))

if __name__ == '__main__':
    app.run()
