from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, validators, EmailField, PasswordField, SubmitField, BooleanField


class RegistrationForm(FlaskForm):
    user = StringField("Username",
                       validators=[validators.DataRequired(), validators.Length(min=3, max=24)])
    email_field = EmailField("Email",
                             validators=[validators.DataRequired(), validators.Email()])
    password_field = PasswordField("Password",
                                   validators=[validators.DataRequired(), validators.EqualTo("confirm_password",
                                                                                             "Passwords must match!")])
    confirm_password = PasswordField("Confirm password")
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email_field = EmailField("Email",
                             validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField("Password",
                             validators=[validators.DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")


class UpdateAccountForm(FlaskForm):
    user = StringField("Username",
                       validators=[validators.DataRequired(), validators.Length(min=3, max=24)])
    email_field = EmailField("Email",
                             validators=[validators.DataRequired(), validators.Email()])
    picture = FileField("Update Profile Picture", validators=[FileAllowed(["jpg", "png", "jpeg"])], id="profile-picture")
    submit = SubmitField("Update")


class RequestResetForm(FlaskForm):
    email_field = EmailField("Email",
                             validators=[validators.DataRequired(), validators.Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password_field = PasswordField("Password",
                                   validators=[validators.DataRequired(), validators.EqualTo("confirm_password",
                                                                                             "Passwords must match!")])
    confirm_password = PasswordField("Confirm password")
    submit = SubmitField("Reset password")
