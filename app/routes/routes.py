import csv
from datetime import datetime, timezone, timedelta
from io import BytesIO, StringIO
from flask import Blueprint, abort, render_template, request, redirect, send_file, url_for, flash, session, jsonify
from app import mongo
from bson import ObjectId
from ..utils.decorators import login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app.services.mqtt_service import mqtt
from ..config import MQTT_TOPIC

main = Blueprint("main", __name__)

TZ = timezone(timedelta(hours=7))  # nếu dữ liệu ts theo UTC+7, chỉnh cho khớp

def _parse_date_yyyy_mm_dd(s: str):
    """Nhận 'YYYY-MM-DD' (từ input type=date). Trả datetime (naive) tại 00:00."""
    return datetime.strptime(s, "%Y-%m-%d")

def _date_range_to_ts_ms(from_date_str, to_date_str):
    """
    Chuyển khoảng [from, to] ngày -> [start_ms, end_ms] theo mốc 00:00..23:59:59.999
    Giả định from/to là local date (UTC+7). Điều chỉnh theo dữ liệu thực tế của bạn.
    """
    if not from_date_str and not to_date_str:
        return None, None

    if from_date_str:
        d0 = _parse_date_yyyy_mm_dd(from_date_str)
    else:
        # nếu không có from -> rất xa
        d0 = datetime(1970, 1, 1)

    if to_date_str:
        d1 = _parse_date_yyyy_mm_dd(to_date_str)
    else:
        # nếu không có to -> hôm nay
        d1 = datetime.now()

    # Khoảng trong ngày [00:00, 23:59:59.999]
    start_dt = datetime(d0.year, d0.month, d0.day, 0, 0, 0)
    end_dt   = datetime(d1.year, d1.month, d1.day, 23, 59, 59, 999000)

    # Nếu ts của bạn là epoch ms theo UTC hoặc UTC+7?
    # - Nếu ESP32 đóng dấu UTC: dùng .replace(tzinfo=timezone.utc)
    # - Nếu bạn coi date theo local (UTC+7) thì offset về UTC trước khi lấy epoch.
    # Ở đây mình giả định local +7 rồi chuyển về UTC khi tính epoch:
    start_ms = int((start_dt.replace(tzinfo=TZ)).timestamp() * 1000)
    end_ms   = int((end_dt.replace(tzinfo=TZ)).timestamp() * 1000)

    return start_ms, end_ms

def _build_query(device_id, from_date, to_date, only_alert=False):
    q = {"device_id": device_id}
    if only_alert:
        q["level"] = {"$in": ["DANGER"]}

    if from_date and to_date:
        q["date"] = {"$gte": from_date, "$lte": to_date}  # ISO date so sánh theo chuỗi OK
    elif from_date:
        q["date"] = {"$gte": from_date}
    elif to_date:
        q["date"] = {"$lte": to_date}

    return q

@main.route("/api/mqtt/ping")
@login_required
def mqtt_ping():
    cmd = mqtt.last_cmd
    mqtt.last_cmd = None   # đọc xong thì xóa, tránh redirect lặp
    return jsonify({"cmd": cmd or ""})

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
    from_date = (request.args.get("from") or "").strip()
    to_date   = (request.args.get("to") or "").strip()
    device_id = "ESP32-001"

    q = _build_query(device_id, from_date, to_date, only_alert=True)

    cur = (mongo.db.mq2_data
           .find(q, {"_id": 0})
           .sort([("date", -1), ("time", -1)])   # thay vì sort("ts", -1)
           .limit(500))

    rows = []
    for d in cur:
        rows.append({
            "date": d.get("date", ""),
            "time": d.get("time", ""),
            "ppm":  d.get("ppm", 0),
            "level": d.get("level", "NORMAL"),
        })

    return render_template("alert_history.html",
                           rows=rows,
                           from_date=from_date,
                           to_date=to_date)

@main.route("/alert_history_export", methods=["GET"])
@login_required
def alert_history_export():
    from_date = (request.args.get("from") or "").strip()
    to_date   = (request.args.get("to") or "").strip()
    device_id = "ESP32-001"

    q = _build_query(device_id, from_date, to_date, only_alert=True)
    cur = (mongo.db.mq2_data
           .find(q, {"_id": 0})
           .sort("ts", -1)
           .limit(5000))

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Time", "Concentration(ppm)", "State"])

    for d in cur:
        ts_ms = int(d.get("ts", 0) or 0)
        if 0 < ts_ms < 10**12:
            ts_ms *= 1000
        dt = datetime.fromtimestamp(ts_ms/1000, tz=TZ) if ts_ms else None
        date_str = d.get("date") or (dt.strftime("%Y-%m-%d") if dt else "")
        time_str = d.get("time") or (dt.strftime("%H:%M") if dt else "")
        writer.writerow([date_str, time_str, d.get("ppm", 0), d.get("level", "")])

    mem = BytesIO(output.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(mem, as_attachment=True,
                     download_name="alert_history.csv",
                     mimetype="text/csv")

from app.models.device import get_device_by_device_id, get_device_by_user_id
@main.route("/configuration", methods=["GET"])
@login_required
def configuration():
    try:
        uid = ObjectId(session["user_id"])
    except Exception:
        abort(401)  # phiên đăng nhập lỗi

    device = get_device_by_device_id("ESP32-001")
    if not device:
        flash("Your account currently does not own any devices.", "warning")
        return render_template("configuration.html", device=None)

    return render_template("configuration.html", device=device)

@main.route("/configuration/sound", methods=["POST"])
@login_required
def configuration_sound():
    device = get_device_by_device_id("ESP32-001")
    if not device:
        flash("Your account currently does not own any devices.", "warning")
        return redirect(url_for("main.configuration"))

    sound_on = (request.form.get("sound") == "on")

    # update database
    mongo.db.devices.update_one({"_id": device["_id"]}, {"$set": {"sound": sound_on}})

    # 2) (Tuỳ chọn) Publish MQTT để thiết bị thực thi ngay
    mqtt.publish(MQTT_TOPIC + "/buzzer", "ON" if sound_on else "OFF")

    flash(f"Sound setting updated: {'ON' if sound_on else 'OFF'}.", "success")
    return redirect(url_for("main.configuration"))

@main.route("/configuration/yellowled", methods=["POST"])
@login_required
def configuration_yellowled():
    uid = ObjectId(session["user_id"])
    device = get_device_by_device_id("ESP32-001")
    if not device:
        flash("Your account currently does not own any devices.", "warning")
        return redirect(url_for("main.configuration"))

    yellowled_on = (request.form.get("yellowled") == "on")

    # update database
    mongo.db.devices.update_one({"_id": device["_id"]}, {"$set": {"yellowled": yellowled_on}})

    # 2) (Tuỳ chọn) Publish MQTT để thiết bị thực thi ngay
    mqtt.publish(MQTT_TOPIC + "/yellowled", "ON" if yellowled_on else "OFF")

    flash(f"Yellow led setting updated: {'ON' if yellowled_on else 'OFF'}.", "success")
    return redirect(url_for("main.configuration"))

@main.route("/configuration/redled", methods=["POST"])
@login_required
def configuration_redled():
    uid = ObjectId(session["user_id"])
    device = get_device_by_device_id("ESP32-001")
    if not device:
        flash("Your account currently does not own any devices.", "warning")
        return redirect(url_for("main.configuration"))

    redled_on = (request.form.get("redled") == "on")

    # update database
    mongo.db.devices.update_one({"_id": device["_id"]}, {"$set": {"redled": redled_on}})

    # 2) (Tuỳ chọn) Publish MQTT để thiết bị thực thi ngay
    mqtt.publish(MQTT_TOPIC + "/redled", "ON" if redled_on else "OFF")

    flash(f"Red led setting updated: {'ON' if redled_on else 'OFF'}.", "success")
    return redirect(url_for("main.configuration"))

@main.route("/analysis", methods=["GET"])
@login_required
def analysis():
    return render_template("analysis.html")
