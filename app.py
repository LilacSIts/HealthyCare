import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from pymongo import MongoClient
from datetime import datetime, timedelta
import jwt
import hashlib

app = Flask(__name__)
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
    role_receive = request.form["role_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.user_patient.find_one(
        {
            "email": email_receive,
            "password": pw_hash,
            "role": role_receive,
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
    if result:
        if role_receive == "doctor":
            return redirect("/doctor")
        elif role_receive == "admin":
            return redirect("/admin")
        else:
            return redirect("/homepatient")
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

@app.route("/addmember/save", methods=["POST"])
def addmember():
    name_receive = request.form.get("name_give")
    poli_receive = request.form.get("poli_give")
    number_receive = request.form.get("number_give")
    role_receive = request.form.get("role_give")
    email_receive = request.form.get("email_give")
    password_receive = request.form.get("password_give")
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    exists = bool(db.user_patient.find_one({"email" : email_receive}))
    doc = {
        "name" : name_receive,
        "poli" : poli_receive,
        "number" : number_receive,
        "role" : role_receive,
        "email" : email_receive,
        "password" : password_hash,
        "profile_name" : name_receive,
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

@app.route("/addmember/check_dup", methods=["POST"])
def check_dupp():
    email_receive = request.form.get("email_give")
    exists = bool(db.user_patient.find_one({"email" : email_receive}))
    return jsonify({"result" : "success", "exists" : exists})

@app.route("/search", methods=["POST"])
def search():
    try:
        search_query = request.form.get("search_query")
        # Cari data berdasarkan nama di MongoDB
        search_results = db.user_patient.find({"name": {"$regex": search_query, "$options": "i"}})
        # Kembalikan hasil pencarian sebagai JSON
        results_list = []
        for result in search_results:
            results_list.append({
                "name": result["name"]
            })
        return jsonify({"result": "success", "search_results": results_list})
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return jsonify({"result": "fail", "msg": "Internal server error"})


@app.route("/doctor")
def doctor():
    return render_template("doctor.html")


@app.route("/homepatient")
def homepatient():
    return render_template("home-patient.html")

@app.route("/mylist")
def mylist():
    return render_template("mylist.html")

@app.route("/konsult")
def konsultasi():
    return render_template("konsult.html")

@app.route("/konsult/save", methods=["POST"])
def konsult():
    fname_receive = request.form.get("fname_give")
    lname_receive = request.form.get("lname_give")
    number_receive = request.form.get("number_give")
    doctor_receive = request.form.get("doctor_give")
    keluhan_receive = request.form.get("keluhan_give")
    email_receive = request.form.get("email_give")
    exists = bool(db.user_patient.find_one({"email" : email_receive}))
    doc = {
        "first_name" : fname_receive,
        "last_name" : lname_receive,
        "number" : number_receive,
        "doctor" : doctor_receive,
        "keluhan" : keluhan_receive,
        "profile_name" : fname_receive,
    }
    db.konsultasi.insert_one(doc)
    return jsonify({"result" : "success", "exists" : exists})

@app.route("/blog")
def blog():
    return render_template("blog.html")

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)