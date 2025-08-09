from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mongo
from bson import ObjectId
from ..utils.decorators import login_required
from werkzeug.security import check_password_hash, generate_password_hash


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
        new_username = request.form.get("username", "").strip()
        new_email = request.form.get("email", "").strip()

        # --- update name/email ---
        updates = {}
        if new_username and new_username != user.get("username"):
            updates["username"] = new_username
        if new_email and new_email != user.get("email"):
            updates["email"] = new_email
        if updates:
            mongo.db.users.update_one({"_id": user["_id"]}, {"$set": updates})
            if "username" in updates:
                session["username"] = updates["username"]
            flash("Profile updated successfully.", "success")

        # --- change password (optional) ---
        current_password = request.form.get("current_password") or ""
        new_password = request.form.get("new_password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        if new_password or confirm_password or current_password:
            if not current_password:
                flash("Please enter your current password to change it.", "danger")
            elif not check_password_hash(user.get("password", ""), current_password):
                flash("Current password is incorrect.", "danger")
            elif len(new_password) < 3:
                flash("New password must be at least 6 characters.", "danger")
            elif new_password != confirm_password:
                flash("New password and confirmation do not match.", "danger")
            elif new_password == current_password:
                flash("New password cannot be the same as current password.", "danger")
            else:
                hashed = generate_password_hash(new_password)
                mongo.db.users.update_one({"_id": user["_id"]}, {"$set": {"password": hashed}})
                flash("Password changed successfully.", "success")

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