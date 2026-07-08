from csv import *
from sqlite3 import *
db = connect('SportsLoans.db')
c = db.cursor()

f = open('Loan.TXT')
lines = reader(f) 
next(lines)        
for line in lines:
    c.execute('''INSERT INTO Loan 
    (LoanID, EquipmentId, StudentID, Qty, LoanDate, ReturnDate) 
    VALUES (?,?,?,?,?,?)''', line)
f.close()
db.commit()
db.close()
