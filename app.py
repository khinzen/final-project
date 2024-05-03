from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError


from helpers import sent_score, posneg


client = OpenAI(
api_key = "LL-JsXHgYMuGCr4WmyOeWH5tVD03o57tlJBFXTJG5v2WsnybEoMB01JzbJWkZ8unAg7",
base_url = "https://api.llama-api.com"
)

#temporary
logged_in = True

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'key'
db = SQLAlchemy(app)
app.app_context().push()

class User(db.Model, UserMixin):
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(20), nullable=False, unique=True)
     password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
     username = StringField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder": "Username"})
     password = PasswordField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder": "Password"})
     submit = SubmitField("Register")

     def validate_username(self, username):
          existing_user_username = User.query.filter_by(username=username.data).first()
          if existing_user_username:
               raise ValidationError("Choose a different username, that one already exists.")

class LoginForm(FlaskForm):
     username = StringField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder": "Username"})
     password = PasswordField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder": "Password"})
     submit = SubmitField("Login")




@app.route('/', methods=["POST", "GET"])
def hello():
    if request.method == "POST":
        prompt = request.form["in"]

        response = client.chat.completions.create(
        model="llama-13b-chat",
        messages=[
            {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
            {"role": "user", "content": f"{prompt}"}
        ]
        )

        answer = response.choices[0].message.content

        stats = sent_score(answer)
        pos, neg = posneg(stats, answer)

        return render_template('result.html', prompt = prompt, answer = answer, pos = pos, neg = neg)
    else:
	    return render_template("home.html")

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()
    return render_template('login.html')

@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    return render_template('register.html')

@app.route('/dashboard', methods=["POST", "GET"])
def dashboard():
    if logged_in == True:
        return render_template('dashboard.html')
    else:
         return render_template('login.html')
