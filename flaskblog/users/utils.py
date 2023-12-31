import os
import secrets

from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + ext
    picture_path = os.path.join(current_app.root_path, "static/img", picture_fn)
    form_picture.save(picture_path)
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def send_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request", sender="noreply@demo.com", recipients=[user.email_field])
    msg.body = f"""
    To reset your password, please follow this link {url_for("users.reset_token", token=token, _external=True)}
    \nIf you did not make this request then simply ignore this email.
    """
    with current_app.app_context():
        mail.send(msg)
