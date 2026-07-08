from flask import Flask, render_template, request   
from sqlite3 import *
from datetime import *

app = Flask(__name__)         

#####################################################
########## TASK 4.3 Create index.html################
#####################################################

@app.route('/') #T4.3 [1m] 3 new routes (index, loan, leaderboard)
def index():
    return render_template('index.html')  
              
#T4.3 [2m] in index.html
#T4.3 [1m] for creating both loan.html and leaderboard.html

#TOTAL for TASK 4.3: 4 marks


#####################################################
########## TASK 4.4 Create loan.html#################
#####################################################

@app.route('/loan')
def loan():
    db = connect('SportsLoans.db')
    c = db.cursor()
    print('connected')
    c.execute('''SELECT Name from Student''')
    names = c.fetchall()
    
    c.execute('''SELECT ID, Name from Equipment''')
    items = c.fetchall()                                             #[1m] T4.4 collect names and items from db
    
    db.close()

    return render_template('loan.html', names = names, items = items) #[1m] T4.4 correct render to loan.html   

# T4.4 [3m] in loan.html
#TOTAL for TASK 4.4: 5 marks




#####################################################
######## TASK 4.4 Create success.html################
#####################################################

@app.route('/success', methods = ['POST'])
def success():
    studentName = request.form.get('StudentName')
    loanItem = request.form.get('eqpt')
    loanQty = int(request.form.get('quantity'))
    loanDate = request.form.get('loandate')         #[1m] T4.5 for correct methods and request.form.get

    print(type(loanItem))
    db = connect('SportsLoans.db')
    c = db.cursor()
    c.execute('''Select ID from Student where Student.Name = ?''', (studentName,))
    studentID = int(c.fetchone()[0])
    print('StudentID is {}'.format(studentID))
    ld = datetime(
        int(loanDate[:4]),
        int(loanDate[5:7]),
        int(loanDate[8:])
        )
    rd = ld + timedelta(days = 2)                   #[1m] T4.5 for correct setting of return date

    ld_string = '{}-{}-{}'.format(ld.strftime('%Y'), ld.strftime('%m'), ld.strftime('%d'))

    rd_string = '{}-{}-{}'.format(rd.strftime('%Y'), rd.strftime('%m'), rd.strftime('%d'))

                                                    #[1m] T4.5 for correct parsing of date
                                              


    c.execute('''INSERT INTO Loan (EquipmentID, StudentID, Qty, LoanDate, ReturnDate) 
    VALUES(?, ?, ?, ?, ?)''', (loanItem, studentID, loanQty, ld_string, rd_string))      #[1m] T4.5 for correct insert


    c.execute('''SELECT sum(Equipment.Points * Loan.Qty) from Equipment, Loan, Student
WHERE Equipment.ID = Loan.EquipmentID
and Loan.StudentID = Student.ID
AND Student.Name = ?''', (studentName,))                                     #[1m] T4.5 for correct retrieval of points

    studentPoints = c.fetchone()[0]

    data = [studentName, rd_string, studentPoints] #[1m] T4.5 for correct data package

    db.commit()
    db.close()
    return render_template('success.html', data = data)                     #[1m] T4.5 for correct render

    #[1m] in success.html
    #TOTAL for TASK 4.5: 8 marks


#####################################################
######## TASK 4.6 Create leaderboard.html############
#####################################################
@app.route('/leaderboard')
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
    
    return render_template('leaderboard.html', leaders = leaders)     # T4.6 [1m] correct render to leaderboard.html


# T4.6 [2m] in leaderboard.html


#TOTAL for TASK 4.6: 3 marks




app.run('127.0.0.1', port = 5001)         

