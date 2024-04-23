from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')