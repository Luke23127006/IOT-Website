from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mongo
from bson import ObjectId
from ..utils.decorators import login_required


main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("login.html")

@main.route("/test-mongo")
def test_mongo():
    print("🛠 mongo.db =", mongo.db)  # check object
    try:
        mongo.db.test.insert_one({"msg": "MongoDB connected!"})
        return "✅ MongoDB connected and data inserted!"
    except Exception as e:
        return f"❌ Error: {e}"
    
@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html", username=session["username"])

@main.route("/account", methods=["GET", "POST"])
@login_required
def account():
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
@login_required
def alert_history():
    return render_template("alert_history.html")

@main.route("/configuration", methods=["GET"])
@login_required
def configuration():    
    return render_template("configuration.html")

@main.route("/analysis", methods=["GET"])
@login_required
def analysis():
    return render_template("analysis.html")