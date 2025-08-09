from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import mongo
from app.models.user import get_user_by_username, create_user

auth = Blueprint("auth", __name__)

from ..utils.security import verify_password, hash_password

def login_user(username: str, password: str):
    user = get_user_by_username(username)
    if user and verify_password(user["password"], password):
        return user
    return None

def signup_user(username: str, email: str, password: str):
    if get_user_by_username(username):
        return None, "Username has been existed!"
    hashed = hash_password(password)
    create_user(username, email, hashed)
    return True, None

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = login_user(username, password)
        if user:
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            flash("Login successfully!", "success")
            return redirect(url_for("main.dashboard"))
        flash("Wrong username or password!", "danger")
        
    return render_template("login.html")

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        ok, err = signup_user(
            request.form.get("username"),
            request.form.get("email"),
            request.form.get("password"),
        )
        if ok:
            flash("Sign up successfully! Please log in.", "success")
            return redirect(url_for("auth.login"))
        flash(err or "Sign up failed.", "danger")
        
    return render_template("signup.html")

@auth.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("Log out successfully!", "success")
    return redirect(url_for("auth.login"))