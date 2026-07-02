from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html') # 1 mark

# HTML file:
# 1 mark for textbox and submit button
# 1 mark for form action

@app.route('/display', methods=['POST']) # 1 mark
def result():
    custname = request.form['custname'] # 1 mark
    conn = sqlite3.connect('COURSES.db') 
    cur = conn.cursor() # 1 mark
    cur.execute("""SELECT Course.Name, Instructor.Name, Registration.Paid
    FROM Customer INNER JOIN 
	(Registration INNER JOIN 
	(Course INNER JOIN Instructor ON Course.InstructorID = Instructor.InstructorID) 
	ON Registration.CourseID = Course.CourseID) 
	ON Customer.CustomerID = Registration.CustomerID 
	WHERE Customer.Name = ?""", (custname,)) # 1 mark
    rows = cur.fetchall() 
    return render_template("display.html", data=rows) # 1 mark

# HTML file
# 1 mark for table (border not required)
# 1 mark for for loop
# 1 mark for data retrieval (if else not required)
	
app.run()

