from flask import *
import sqlite3

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def result():
    stall_name = request.form["stall_name"]
    date = request.form["date"]

    conn = sqlite3.connect("canteen.db")
    conn.row_factory = sqlite3.Row

    sql = """
    SELECT stall.stallID, SUM(dish.price * orderDish.quantity) AS Total
    FROM orderDish
    JOIN dish ON orderDish.dishID = dish.dishID
    JOIN stall ON dish.stallID = stall.stallID
    WHERE stall.stallName = ?  AND orderDish.orderDate = ?
    GROUP BY stall.stallName, orderDish.orderDate;
    """

    cur = conn.execute(sql, (stall_name, date))
    data = cur.fetchone()
    conn.close()

    return render_template("result.html",stall_name = stall_name, date = date, data = data)

if __name__ == "__main__":
    app.run(debug=True)
