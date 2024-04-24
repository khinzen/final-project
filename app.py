from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=["GET"])
def hello():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/result')
def result():
    return render_template('result.html')