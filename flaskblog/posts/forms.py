from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, validators


class PostForm(FlaskForm):
    title = StringField("Title", validators=[validators.DataRequired()])
    content = TextAreaField("Context", validators=[validators.DataRequired()])
    submit = SubmitField("Post")


