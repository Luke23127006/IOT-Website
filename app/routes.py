from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from app import mongo
from bson import ObjectId

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("login.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = mongo.db.users.find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Sai tên đăng nhập hoặc mật khẩu!", "danger")

    return render_template("login.html")

@main.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = mongo.db.users.find_one({"username": username})
        if existing_user:
            flash("Tên người dùng đã tồn tại!", "danger")
            return redirect(url_for("main.signup"))

        hashed_pw = generate_password_hash(password)
        mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password": hashed_pw
        })

        flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
        return render_template("login.html")

    return render_template("signup.html")


@main.route("/test-mongo")
def test_mongo():
    print("🛠 mongo.db =", mongo.db)  # check object
    try:
        mongo.db.test.insert_one({"msg": "MongoDB connected!"})
        return "✅ MongoDB connected and data inserted!"
    except Exception as e:
        return f"❌ Error: {e}"
    
@main.route("/dashboard")
def dashboard():
    if "username" not in session:
        flash("Vui lòng đăng nhập trước.", "warning")
        return redirect(url_for("main.login"))
    
    return render_template("dashboard.html", username=session["username"])

@main.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("Đăng xuất thành công!", "success")
    return redirect(url_for("main.login"))

@main.route("/account", methods=["GET", "POST"])
def account():
    if "user_id" not in session:
        flash("Vui lòng đăng nhập trước.", "warning")
        return redirect(url_for("main.login"))

    user = mongo.db.users.find_one({"_id": ObjectId(session["user_id"])})

    if request.method == "POST":
        new_username = request.form.get("username")
        new_email = request.form.get("email")

        if new_username:
            mongo.db.users.update_one({"_id": user["_id"]}, {"$set": {"username": new_username}})
            session["username"] = new_username
            flash("Cập nhật tên người dùng thành công!", "success")

        if new_email:
            mongo.db.users.update_one({"_id": user["_id"]}, {"$set": {"email": new_email}})
            flash("Cập nhật email thành công!", "success")

        return redirect(url_for("main.account"))

    return render_template("account.html", user=user)

@main.route("/alert_history", methods=["GET"])
def alert_history():
    return render_template("alert_history.html")

@main.route("/configuration", methods=["GET", "POST"])
def configuration():
    return render_template("configuration.html")

@main.route("/analysis", methods=["GET"])
def analysis():
    return render_template("analysis.html")