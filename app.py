from flask import Flask, render_template, request, redirect, url_for, session
from openai import OpenAI

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

from helpers import sent_score, posneg, overall_sentiment


client = OpenAI(
api_key = "LL-JsXHgYMuGCr4WmyOeWH5tVD03o57tlJBFXTJG5v2WsnybEoMB01JzbJWkZ8unAg7",
base_url = "https://api.llama-api.com"
)


app = Flask(__name__)


bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'key'
db = SQLAlchemy(app)
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
     return User.query.get(int(user_id))

class User(db.Model, UserMixin):
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(20), nullable=False, unique=True)
     password = db.Column(db.String(80), nullable=False)

class Prompts(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     user = db.Column(db.String)
     input = db.Column(db.String(1000), nullable=False, unique=False)
     output = db.Column(db.String(1000), nullable=False)
     overall = db.Column(db.Integer)
     
logged_in = False

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






@app.route('/', methods=["GET"])
def hello():
	return render_template("home.html")

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/result', methods=["POST", "GET"])
def result():
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

        # consider bundling all inputs into dictionary

        stats = sent_score(answer)
        pos, neg = posneg(stats, answer)
        overall = overall_sentiment(stats)

        session['prompt'] = prompt
        session['answer'] = answer
        session['overall'] = overall
        
    

        return render_template('result.html', prompt = prompt, answer = answer, pos = pos, neg = neg, overall = overall)

@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
         user = User.query.filter_by(username=form.username.data).first()
         if user:
              session['user'] = user.username
              if bcrypt.check_password_hash(user.password, form.password.data):
                   login_user(user)
                   return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
         hashed_password = bcrypt.generate_password_hash(form.password.data)
         new_user = User(username=form.username.data, password=hashed_password)
         db.session.add(new_user)
         db.session.commit()
         return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/dashboard', methods=["POST", "GET"])
@login_required
def dashboard():
    # try:
    finalUserPrompts = []
    userPrompts = Prompts.query.filter_by(user = session['user']).all()
    for entry in userPrompts:
        prompt = {}
        prompt["Search"] = entry.id
        prompt["Input"] = entry.input
        prompt["Output"] = entry.output
        prompt["Score"] = entry.overall
        finalUserPrompts.append(prompt)
             
    # except:
    #     finalUserPrompts = [{"Input": "see input here", "Output": "see output here"}]
    return render_template('dashboard.html', userPrompts = finalUserPrompts)

@app.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
     logout_user()
     return redirect(url_for('login'))

@app.route('/save', methods=["POST", "GET"])
@login_required
def save():
    if len(session['prompt']) > 1000:
        session['prompt'] = session['prompt'][0:999]

    if len(session['answer']) > 1000:
        session['answer'] = session['answer'][0:999]

    save_prompt = Prompts(user = session['user'], input = session['prompt'], output = session['answer'], overall = session['overall'])
    db.session.add(save_prompt)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete/<id>', methods=["POST", "GET"])
@login_required
def delete(id):
    delete_prompt = Prompts.query.get_or_404(id)
    db.session.delete(delete_prompt)
    db.session.commit()

    return redirect(url_for('dashboard'))

        
     

