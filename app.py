from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI


client = OpenAI(
api_key = "LL-JsXHgYMuGCr4WmyOeWH5tVD03o57tlJBFXTJG5v2WsnybEoMB01JzbJWkZ8unAg7",
base_url = "https://api.llama-api.com"
)



app = Flask(__name__)

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

        return render_template('result.html', prompt = prompt, answer = answer)
    else:
	    return render_template("home.html")

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=["POST", "GET"])
def login():
    return render_template('login.html')

@app.route('/dashboard', methods=["POST", "GET"])
def dashboard():
    return render_template('dashboard.html')
