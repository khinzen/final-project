from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=["POST", "GET"])
def hello():
    if request.method == "POST":
        prompt = request.form["in"]
        return render_template('result.html', prompt = prompt)
    else:
	    return render_template("home.html")

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')
