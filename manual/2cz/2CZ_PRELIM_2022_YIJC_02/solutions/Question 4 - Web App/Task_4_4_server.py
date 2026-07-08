from flask import Flask, render_template, request   
from sqlite3 import *
from datetime import *

app = Flask(__name__)                               

@app.route('/')
def index():
    return render_template('index.html')            

@app.route('/loan')
def loan():
    db = connect('SportsLoans.db')
    c = db.cursor()
    print('connected')
    c.execute('''SELECT Name from Student''')
    names = c.fetchall()
    
    c.execute('''SELECT ID, Name from Equipment''')
    items = c.fetchall()
    
    db.close()

    return render_template('loan.html', names = names, items = items)  

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html')

@app.route('/success', methods = ['POST'])
def success():
    return ""

app.run('127.0.0.1', port = 5000)
