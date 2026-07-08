#1 mark(TASK 4.3) - all Flask related statement are present (import statements, creation of flask object, starting the server)
#Importing all the required libraries
import flask
from flask import *
import sqlite3

app = flask.Flask(__name__) #create a Flask object 


@app.route('/')  #1 mark(TASK 4.3) - correct implementation of index method
def index():
    return render_template('index.html') #displaying index.html


@app.route('/latecoming_report')  #1 mark(TASK 4.4) - correct implementation of latecoming_report method and connection to db to extract records
def latecoming_report():
    #connecting to given sqlite database and extracting relevant records
    connection = sqlite3.connect("Discipline.db")

    #querying the number of latecoming by students, showing only those with 2 or more latecoming
    cursor = connection.execute('''SELECT Name, Class, Count(*) FROM Student
                                INNER JOIN Latecoming ON Student.StudentID = Latecoming.StudentID
                                GROUP BY Name
                                HAVING Count(*) > 2
                                ORDER BY Count(*) DESC;''')
    records_by_student = cursor.fetchall()


    #querying the number of latecoming by class
    cursor = connection.execute('''SELECT Class, Count(*) FROM Student
                                INNER JOIN Latecoming ON Student.StudentID = Latecoming.StudentID
                                GROUP BY Class
                                ORDER BY CLass;''')
    records_by_class = cursor.fetchall()

    connection.close()

    #1 mark(TASK 4.4) - render correct html template with sending records to html file (give the mark if either latecoming_report or detention_tracker html file has this)     
    return render_template('latecoming_report.html', html_latecoming_records_by_student = records_by_student, html_latecoming_records_by_class = records_by_class)


@app.route('/process_detention', methods=['GET','POST']) #decorator #1 mark(TASK 4.5) - correct implementation of process_detention method - indicated methods GET and POST - default only allows GET methods
def process_detention():

    if 'latecomingid' in request.form: #checking if any html form input with the name 'latecomingid'
        latecoming_id = request.form['latecomingid'] #1 mark(TASK 4.5) - extracting what user keyed in for the html form input 'latecomingid'

        #1 mark(TASK 4.5) - connecting to given sqlite database and updating correct record in database
        connection = sqlite3.connect("Discipline.db")
        connection.execute("UPDATE Latecoming SET Detention_Completion_Status = 'True' WHERE LatecomingID = ?",(latecoming_id,))

        # Step 4 - make changes permanent
        connection.commit()

    #1 mark(TASK 4.5) - connecting to given sqlite database and extracting correct records in database
    connection = sqlite3.connect("Discipline.db")    
    cursor = connection.execute('''SELECT LatecomingID, Name, Class, Latecoming_Date, Detention_Date, Detention_Completion_Status
                                FROM Student INNER JOIN Latecoming ON Student.StudentID = Latecoming.StudentID;''')
    detention_records = cursor.fetchall()

    connection.close()

    return render_template('detention_tracker.html', html_detention_records = detention_records)


	
if __name__ == "__main__":
    app.run() #calling the Flask object’s run() method to start the server
