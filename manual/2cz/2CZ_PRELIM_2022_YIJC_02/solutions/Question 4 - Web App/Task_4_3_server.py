from flask import Flask, render_template, request   
from sqlite3 import *

app = Flask(__name__)                               

@app.route('/')
def index():
    return render_template('index.html')            

@app.route('/loan')
def loan():
    return render_template('loan.html')     

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

app.run('127.0.0.1', port = 5000)
