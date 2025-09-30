from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length

class SignupForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class CardForm(FlaskForm):
    name = StringField("Card Name", validators=[DataRequired()])
    submit = SubmitField("Create Card")

class TodoForm(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    choices = SelectField("Card", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save Task")
