import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, jsonify
from pymongo import MongoClient
from datetime import datetime, timedelta
import jwt
import hashlib

app = Flask(__name__)

MONGODB_CONNECTION_STRING = 'mongodb+srv://test:sparta@cluster0.dj3jxz6.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.dbsparta_plus_week4

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = '/static/profile_pics'

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)



SECRET_KEY = 'STEALY'
MONGODB_URL = os.environ.get("MONGODB_URL")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URL)
db = client.Stealy

TOKEN_KEY = 'mytoken'


@app.route('/', methods=['GET'])
def home(): 
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    fname_receive = request.form.get("fname_give")
    lname_receive = request.form.get("lname_give")
    email_receive = request.form.get("email_give")
    password_receive = request.form.get("password_give")
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    exists = bool(db.user_patient.find_one({"email" : email_receive}))
    doc = {
        "first_name" : fname_receive,
        "last_name" : lname_receive,
        "email" : email_receive,
        "password" : password_hash,
        "profile_name" : fname_receive,
        "profile_pic" : "",
        "profile_pic_real" : "profile_pics/profile_placeholder.png",
        "additional_details" : "",
        "age" : "",
        "mobile_number" : "",
        "country" : "",
        "state_region" : ""
    }
    db.user_patient.insert_one(doc)
    return jsonify({"result" : "success", "exists" : exists})

@app.route("/sign_up/check_dup", methods=["POST"])
def check_dup():
    email_receive = request.form.get("email_give")
    exists = bool(db.user_patient.find_one({"email" : email_receive}))
    return jsonify({"result" : "success", "exists" : exists})

@app.route("/login", methods=["GET"])
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)

@app.route("/sign_in", methods=["POST"])
def sign_in():
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.user_patient.find_one(
        {
            "email": email_receive,
            "password": pw_hash,
        }
    )
    if result:
        session['email_patient'] = email_receive
    if result:
        payload = {
            "id": email_receive,\
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    # id/password combination cannot be found
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that email/password combination",
            }
        )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/doctor")
def doctor():
    return render_template("doctor.html")

@app.route("/mylist")
def mylist():
    return render_template("mylist.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)