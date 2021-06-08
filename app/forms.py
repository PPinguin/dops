from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, ValidationError, EqualTo
from wtforms_components import ColorField
from wtforms.fields.html5 import EmailField
from app.models import User

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_again = PasswordField("Repeat password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user is None:
            raise ValidationError('This email address has been registered already.')

class EditRiddleForm(FlaskForm):
    body = TextAreaField("Body", validators=[DataRequired()])
    answer = StringField("Answer", validators=[DataRequired()])
    theme = ColorField("Theme")
    submit = SubmitField("Submit")

class SearchForm(FlaskForm):
    body = StringField("Body", validators=[DataRequired()])
    submit = SubmitField("Search")