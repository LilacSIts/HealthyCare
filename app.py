import os
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from pymongo import MongoClient
from datetime import datetime, timedelta
import jwt
import hashlib
from bson.objectid import ObjectId
import json

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = '/static/profile_pics'

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)



SECRET_KEY = 'healthkey1223'
app.secret_key = 'tessss'
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
    # role_receive = request.form["role_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.user_patient.find_one(
        {
            "email": email_receive,
            "password": pw_hash,
           # "role": role_receive, coba di close dulu kali?kaga bntr
        }
    )
    if result:
        session['patient'] = email_receive
    if result:
        payload = {
            "id": email_receive,
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
        #id/password combination cannot be found
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

count = 0

@app.route("/addmember/save", methods=["POST"])
def addmember():
    global count  # Use the global keyword to modify the global count variable
    count += 1  # Increment the count

    name_receive = request.form.get("name_give")
    poli_receive = request.form.get("poli_give")
    number_receive = request.form.get("number_give")
    role_receive = request.form.get("role_give")
    email_receive = request.form.get("email_give")
    num = count + 1
    password_receive = request.form.get("password_give")
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    exists = bool(db.user_patient.find_one({"email" : email_receive}))
    doc = {
        "num": num,
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

@app.route("/addmember", methods=["GET"])
def addmember_get():
    # Tentukan peran yang diizinkan
    allowed_roles = ['Doctor', 'Admin', 'doctor', 'admin']

    # Tentukan kueri untuk hanya mendapatkan dokumen dengan peran yang diizinkan
    query = {'role': {'$in': allowed_roles}}
    doctor_list = list(db.user_patient.find(query, {'_id': False}))
    for doctor in doctor_list:
        for key, value in doctor.items():
            if not value:
                doctor[key] = "-"
    return jsonify({'doctor': doctor_list})

@app.route("/member/delete", methods=["POST"])
def member_delete():
    delete_receive = request.form["delete_give"]
    db.user_patient.delete_one(
        {'num': int(delete_receive)}
    )
    return jsonify({'msg': 'Delete done!'})

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


@app.route("/home-patient")
def homepatient():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        return render_template("patient/home-patient.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Token Expired"
        return redirect(url_for("home", msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "Error"
        return redirect(url_for("home", msg=msg))

@app.route("/mylist")
def mylist():
    return render_template("/patient/mylist.html")

@app.route("/konsult")
def konsultasi():
    return render_template("/patient/konsult.html")

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
# File Doctor
#home page for doctor
@app.route("/Home-doctor.html")
def home_doctor():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_doctor.find_one({"email" : payload.get("id")})
        return render_template("/doctor/Home-doctor.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("login-doctor",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("login-doctor",msg=msg))

#accept My List from doctor
@app.route("/update_appointment", methods=["POST"])
def update_appointment():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        message_receive = request.form.get("message_give")
        date_receive = request.form.get("date_give")
        time1_receive = request.form.get("time1_give")
        time2_receive = request.form.get("time2_give")
        id_receive = request.form.get("id_give")
        new_doc = {
            "doc_message" : message_receive,
            "date_app" : date_receive,
            "timestart_app" : time1_receive,
            "timeend_app" : time2_receive,
            "status" : 1
        }

        db.appointment_patient.update_one(
            {"_id" : ObjectId(id_receive)},
            {"$set" : new_doc}
        )
        return jsonify({
            "result" : "success",
            "msg" : "Appointment Accepted"
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

#cancel My List from doctor
@app.route("/cancel_appointment", methods=["POST"])
def cancel_appointment():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        message_receive = request.form.get("message_give")
        id_receive = request.form.get("id_give")
        new_doc = {
            "doc_message" : message_receive,
            "status" : 3
        }

        db.appointment_patient.update_one(
            {"_id" : ObjectId(id_receive)},
            {"$set" : new_doc}
        )
        return jsonify({
            "result" : "success",
            "msg" : "Appointment Declined"
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

#User info for doctor
@app.route("/info-doctor.html")
def info_doctor():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_doctor.find_one({"email" : payload.get("id")})
        return render_template("doctor/info-doctor.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("login_doctor",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("login_doctor",msg=msg))

#User edit for doctor
@app.route("/edit-doctor")
def user_doctor():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_doctor.find_one({"email" : payload.get("id")})
        return render_template("doctor/Info-doctor.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("login_doctor",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("login_doctor",msg=msg))

#doctor server edit
@app.route("/update_docprofile", methods=["POST"])
def update_docprofile():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        email = payload.get("id")
        mobilenumber_receive = request.form.get("mobilenumber_give")
        country_receive = request.form.get("country_give")
        stateregion_receive = request.form.get("stateregion_give")
        additionaldetails_receive = request.form.get("additionaldetails_give")
        new_doc = {
            "phone_number" : mobilenumber_receive,
            "address_country" : country_receive,
            "address_stateregion" : stateregion_receive,
            "additional_details" : additionaldetails_receive,
        }

        if "file_give" in request.files:
            file = request.files.get("file_give")
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{email}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path

        db.user_doctor.update_one(
            {"email" : email},
            {"$set" : new_doc}
        )
        # db.posts.update_one(
        #     {"email" : email},
        #     {"$set" : new_doc}
        # )
        return jsonify({
            "result" : "success",
            "msg" : "Your profile has been updated"
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)