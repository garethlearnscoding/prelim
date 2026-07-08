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

@app.route('/success', methods = ['POST'])
def success():
    studentName = request.form.get('StudentName')
    loanItem = request.form.get('eqpt')
    loanQty = int(request.form.get('quantity'))
    loanDate = request.form.get('loandate')

    db = connect('SportsLoans.db')
    c = db.cursor()
    c.execute('''Select ID from Student where Student.Name = ?''', (studentName,))
    studentID = int(c.fetchone()[0])

    ld = datetime(
        int(loanDate[:4]),
        int(loanDate[5:7]),
        int(loanDate[8:])
        )
    rd = ld + timedelta(days = 2)

    ld_string = '{}-{}-{}'.format(ld.strftime('%Y'), ld.strftime('%m'), ld.strftime('%d'))

    rd_string = '{}-{}-{}'.format(rd.strftime('%Y'), rd.strftime('%m'), rd.strftime('%d'))

    c.execute('''INSERT INTO Loan (EquipmentID, StudentID, Qty, LoanDate, ReturnDate) 
    VALUES(?, ?, ?, ?, ?)''', (loanItem, studentID, loanQty, ld_string, rd_string))


    c.execute('''SELECT sum(Equipment.Points * Loan.Qty) from Equipment, Loan, Student
WHERE Equipment.ID = Loan.EquipmentID
and Loan.StudentID = Student.ID
AND Student.Name = ?''', (studentName,))

    studentPoints = c.fetchone()[0]

    data = [studentName, rd_string, studentPoints]

    db.commit()
    db.close()
    return render_template('success.html', data = data)

@app.route('/leaderboard', methods = ['GET', 'POST'])
def leaderboard():
        
    db = connect('SportsLoans.db')
    c = db.cursor()
    c.execute('''SELECT Student.Name, sum(Equipment.Points * Loan.Qty)
FROM Loan, Equipment, Student
WHERE Loan.EquipmentID = Equipment.ID
AND Student.ID = Loan.StudentID
GROUP by Student.Name
ORDER by sum(Equipment.Points * Loan.Qty) DESC
LIMIT 3''')

    leaders = c.fetchall()

    if request.method == 'POST':
        formname = request.form['entername']
        c.execute('''SELECT Student.Name, sum(Equipment.Points * Loan.Qty)
FROM Loan, Equipment, Student
WHERE Loan.EquipmentID = Equipment.ID
AND Student.ID = Loan.StudentID
AND Student.Name = ?''',(formname,))
        student = c.fetchone()
        if student == (None, None):
            student = ("-","-")
    else:
        student = ("-","-")
    
    return render_template('leaderboard.html', leaders = leaders, student = student)     # T4.6 [1m] correct render to leaderboard.html

app.run('127.0.0.1', port = 5000)
