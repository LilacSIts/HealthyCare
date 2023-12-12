from flask import Flask, render_template, request, session, jsonify
import jwt

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home(): 
    return render_template("index.html")

@app.route("/login", methods=["GET"])
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/doctor")
def doctor():
    return render_template("doctor.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)