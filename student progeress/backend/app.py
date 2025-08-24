from flask import Flask, request, redirect, url_for, session, flash, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

app = Flask(__name__, template_folder="templates")  # Make sure templates folder is used
app.secret_key = "supersecretkey"

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://lokeshai2005:nqMFpORAKIt3rnzT@studentsincet.z52jo2f.mongodb.net/?retryWrites=true&w=majority&appName=studentsincet")
db = client["studentdb"]
users = db["users"]

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/signup", methods=["POST"])
def signup():
    fullname = request.form["fullname"]
    reg_no = request.form["reg_no"]
    password = request.form["password"]

    existing = users.find_one({"reg_no": reg_no})
    if existing:
        flash("Register Number already exists!", "danger")
        return redirect(url_for("index"))

    hashed_pw = generate_password_hash(password)
    users.insert_one({
        "fullname": fullname,
        "reg_no": reg_no,
        "password": hashed_pw,
        "department": "CSE",
        "gpa": 0,
        "cgpa": 0,
        "marks": {"Maths": 0, "Data Structures": 0, "DBMS": 0, "OS": 0}
    })
    flash("Account created successfully! Please log in.", "success")
    return redirect(url_for("index"))

@app.route("/login", methods=["POST"])
def login():
    reg_no = request.form["reg_no"]
    password = request.form["password"]

    user = users.find_one({"reg_no": reg_no})
    if user and check_password_hash(user["password"], password):
        session["user_id"] = str(user["_id"])
        session["fullname"] = user["fullname"]
        session["reg_no"] = user["reg_no"]
        return redirect(url_for("dashboard"))
    else:
        flash("Invalid Register Number or Password!", "danger")
        return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("index"))

    user = users.find_one({"reg_no": session["reg_no"]})
    if not user:
        return redirect(url_for("index"))

    return render_template(
        "dashboard.html",
        fullname=user.get("fullname", "Unknown"),
        reg_no=user.get("reg_no", "N/A"),
        department=user.get("department", "Unknown"),
        gpa=user.get("gpa", 0),
        cgpa=user.get("cgpa", 0),
        maths=user.get("marks", {}).get("Maths", 0),
        ds=user.get("marks", {}).get("Data Structures", 0),
        dbms=user.get("marks", {}).get("DBMS", 0),
        os=user.get("marks", {}).get("OS", 0),
        marks=user.get("marks", {})
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
