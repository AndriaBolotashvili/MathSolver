from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length

# რეგისტრაცია
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4)])
    submit = SubmitField("Register")

# ლოგინი
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# ფორუმის პოსტი
class PostForm(FlaskForm):
    title = StringField("სათაური", validators=[DataRequired()])
    content = TextAreaField("ტექსტი", validators=[DataRequired()])
    submit = SubmitField("დამატება")

# სამკუთხედის ფართობი
class TriangleForm(FlaskForm):
    a = FloatField("გვერდი a", validators=[DataRequired()])
    b = FloatField("გვერდი b", validators=[DataRequired()])
    c = FloatField("გვერდი c", validators=[DataRequired()])
    submit = SubmitField("გამოთვლა")

# კვადრატული განტოლება
class QuadraticForm(FlaskForm):
    a = FloatField("a", validators=[DataRequired()])
    b = FloatField("b", validators=[DataRequired()])
    c = FloatField("c", validators=[DataRequired()])
    submit = SubmitField("გამოთვლა")

# წრეწირი
class CircleForm(FlaskForm):
    r = FloatField("რადიუსი r", validators=[DataRequired()])
    submit = SubmitField("გამოთვლა")

# ტრაპეცია
class TrapezoidForm(FlaskForm):
    a = FloatField("ქვედა ბაზა a", validators=[DataRequired()])
    b = FloatField("ზედა ბაზა b", validators=[DataRequired()])
    h = FloatField("სიმაღლე h", validators=[DataRequired()])
    submit = SubmitField("გამოთვლა")

# კომენტარი
class CommentForm(FlaskForm):
    content = TextAreaField("კომენტარი", validators=[DataRequired()])
    submit = SubmitField("დამატება")
