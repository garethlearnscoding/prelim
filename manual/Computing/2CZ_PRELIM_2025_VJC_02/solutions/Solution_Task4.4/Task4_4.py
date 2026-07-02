# Task 4.4

from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        bus_stop = request.form.get('busstop')

        conn = sqlite3.connect('BUSROUTES.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT RoadName, Description
            FROM Stop
            WHERE BusStopCode = ?
        ''', (bus_stop,))
        stop_details = cursor.fetchone()

        if not stop_details:
            return render_template('result.html', error="Invalid bus stop code")

        cursor.execute('''
            SELECT Route.ServiceNo, Route.Operator
            FROM Route
            WHERE Route.BusStopCode = ?
            ORDER BY Route.ServiceNo
        ''', (bus_stop,))
        services = cursor.fetchall()
          
        conn.close()

        return render_template('result.html',
                               stop_code=bus_stop,
                               road_name=stop_details[0],
                               description=stop_details[1],
                               services=services)

    return render_template('index.html')

if __name__ == '__main__':
    app.run()
