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


#sets up database for logging in and saving the searches of users

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

#creates structure for databank of users 
class User(db.Model, UserMixin):
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(20), nullable=False, unique=True)
     password = db.Column(db.String(80), nullable=False)

#creates structure for databank of saved promps and responses for each user
class Prompts(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     user = db.Column(db.String)
     input = db.Column(db.String(1000), nullable=False, unique=False)
     output = db.Column(db.String(1000), nullable=False)
     overall = db.Column(db.Integer)
     

#code for registration
class RegisterForm(FlaskForm):
     username = StringField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder": "Username"})
     password = PasswordField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder": "Password"})
     submit = SubmitField("Register")

     def validate_username(self, username):
          existing_user_username = User.query.filter_by(username=username.data).first()
          if existing_user_username:
               raise ValidationError("Choose a different username, that one already exists.")

#code for login
class LoginForm(FlaskForm):
     username = StringField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder": "Username"})
     password = PasswordField(validators=[InputRequired(),Length(min=4, max=20)], render_kw={"placeholder": "Password"})
     submit = SubmitField("Login")





#displays the home page when app is initially run
@app.route('/', methods=["GET"])
def hello():
	return render_template("home.html")

#this provides the base that the other pages are built on, with the navigation bar at the top
@app.route('/index')
def index():
    return render_template('index.html')

#this gets the result and routes to the page where that is displayed
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

#login page
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

#register page
@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
         hashed_password = bcrypt.generate_password_hash(form.password.data)
         new_user = User(username=form.username.data, password=hashed_password)
         db.session.add(new_user)
         db.session.commit()
         user = User.query.filter_by(username=form.username.data).first()
         if user:
            session['user'] = user.username
            login_user(user)
            return redirect(url_for('dashboard'))

    return render_template('register.html', form=form)

#the dashboard, where logged in users can see saved searches, and can log out
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
        if entry.overall == 1:
            prompt["Score"] = "Positive"
        elif entry.overall == 2:
            prompt["Score"] = "Neutral"
        else:
             prompt["Score"] = "Negative"
        finalUserPrompts.append(prompt)
             
    # except:
    #     finalUserPrompts = [{"Input": "see input here", "Output": "see output here"}]
    return render_template('dashboard.html', userPrompts = finalUserPrompts)

#the route behind the logout button, returns user to the login page
@app.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
     logout_user()
     return redirect(url_for('login'))

#the route behind the save button on the result page, sends user to the dashboard
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

#the route behind the delete button
@app.route('/delete/<int:id>', methods=["POST", "GET"])
@login_required
def delete(id):
    delete_prompt = Prompts.query.get_or_404(id)
    db.session.delete(delete_prompt)
    db.session.commit()
    return redirect(url_for('dashboard'))
    

        
     

