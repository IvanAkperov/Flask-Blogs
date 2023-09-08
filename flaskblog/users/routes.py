from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError

from flaskblog import bcrypt, db
from flaskblog.models import User, Post
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flaskblog.users.utils import save_picture, send_email

users = Blueprint("users", __name__)


@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.homepage"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password_field.data).decode("utf-8")
        user = User(user=form.user.data, email_field=form.email_field.data, password_field=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash(f"Dear {form.user.data},\nYour account has been created. Now you are able to log in!", "success")
            return redirect(url_for("users.login"))
        except IntegrityError:
            db.session.rollback()
            flash("Sorry, this username or email is already taken. Choose a different one", "danger")
            return render_template("register.html", title="Registration page", form=form)
    else:
        return render_template("register.html", title="Registration page", form=form)


@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.homepage"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_field=form.email_field.data).first()
        if user and bcrypt.check_password_hash(user.password_field, form.password.data):
            login_user(user=user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.homepage"))
        flash("Check your email and password!", "danger")

    return render_template("login.html", title="Log In", form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.homepage"))


@users.route("/account", methods=["POST", "GET"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        user = User.query.filter_by(user=form.user.data).first()
        if not user or (user.user == current_user.user and user.email_field == current_user.email_field):
            current_user.user = form.user.data
            current_user.email_field = form.email_field.data
            db.session.commit()
            flash("Your account has been updated!", "success")
            return redirect(url_for("users.account"))
        else:
            flash("Sorry, this username or email is already taken. Choose a different one", "danger")
            return redirect(url_for("users.account"))
    elif request.method == "GET":
        form.user.data = current_user.user
        form.email_field.data = current_user.email_field
    img_file = url_for("static", filename=f"img/{current_user.image_file}")
    return render_template("account.html", title="Your account", img_file=img_file, form=form)


@users.route("/user/<string:username>")
def get_user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(user=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("user_posts.html", posts=posts, user=user)


@users.route("/reset_password", methods=["POST", "GET"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.homepage"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_field=form.email_field.data).first()
        send_email(user)
        flash("An email has been sent to reset your password", "info")
        return redirect(url_for("users.login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@users.route("/reset_password/<token>", methods=["POST", "GET"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.homepage"))
    user = User.verify_reset_token(token=token)
    if not user:
        flash("This token is invalid or expired", "warning")
        return redirect(url_for("users.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password_field.data).decode("utf-8")
        user.password_field = hashed_password
        db.session.commit()
        flash(f"Your password has been updated. Now you are able to log in!", "success")
        return redirect(url_for("users.login"))
    return render_template("reset_token.html", title="Reset Password", form=form)
