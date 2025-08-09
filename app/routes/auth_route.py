from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from app import mongo
from app.models.user import get_user_by_username, create_user, get_user_by_id

auth = Blueprint("auth", __name__)

from ..utils.security import verify_password, hash_password

def login_user(username: str, password: str):
    user = get_user_by_username(username)
    if user and verify_password(user["password"], password):
        return user
    return None

def signup_user(username: str, email: str, password: str):
    if get_user_by_username(username):
        return None, "Tên người dùng đã tồn tại!"
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
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("main.dashboard"))
        flash("Sai tên đăng nhập hoặc mật khẩu!", "danger")
        
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
            flash("Đăng ký thành công! Vui lòng đăng nhập.", "success")
            return redirect(url_for("auth.login"))
        flash(err or "Đăng ký thất bại.", "danger")
        
    return render_template("signup.html")

@auth.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("Đăng xuất thành công!", "success")
    return redirect(url_for("auth.login"))