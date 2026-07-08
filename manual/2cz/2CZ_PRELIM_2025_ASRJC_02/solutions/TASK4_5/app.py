from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    transactions = []
    search_name = ""

    if request.method == "POST":
        search_name = request.form.get("user_name", "").strip()  # get data from inputbox
        if len(search_name) > 0:
            # connect to DB to extract data
            conn = sqlite3.connect("USER_DATA.db")
            cursor = conn.cursor()

            # calculate 90 days before
            curr_date = datetime.now()  # using system time (expected)
            curr_date = datetime(2025, 8, 20)  # hardcoded date for reference
            start_date = curr_date - timedelta(days=90)
            start_date_str = start_date.strftime("%Y-%m-%d")

            query = """
            SELECT User.name, Credit.dt_transaction, Credit.type, Credit.amt
            FROM User
            INNER JOIN Credit ON User.user_id = Credit.user_id
            WHERE User.name = ?
            AND Credit.dt_transaction >= ?
            ORDER BY Credit.dt_transaction DESC;
            """

            cursor.execute(query, (search_name, start_date_str))
            transactions = cursor.fetchall()
            conn.close()
    
    return render_template("index.html", transactions=transactions, search_name=search_name)


if __name__ == "__main__":
    app.run(port=5678)
            
