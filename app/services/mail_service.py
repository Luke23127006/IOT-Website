from flask_mail import Mail, Message
mail = Mail()

def send_alert(subject: str, html: str, recipients: list[str]):
    from flask import current_app
    with current_app.app_context():
        msg = Message(subject=subject, recipients=recipients, html=html)
        mail.send(msg)