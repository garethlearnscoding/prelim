import sqlite3

DB = "canteen.db"

def mk_student_id(nric, name):
    # last 4 of NRIC + first 4 of name (no spaces), uppercase
    last4 = nric[-4:]
    first4 = "".join(name.split())[:4]
    return (last4 + first4).upper()

def load_student(path="STUDENT.txt"):
    conn = sqlite3.connect(DB)

    with open(path, "r") as f: #closes automatically
        next(f) #skips header
        for line in f:
            line = line.strip()
            if not line: 
                continue
            nric, name, phone = [x.strip() for x in line.split(",")]
            sid = mk_student_id(nric, name)
            conn.execute(
                "INSERT INTO student(studentID,name,phoneNo) VALUES(?,?,?)",
                (sid, name, phone),
            )

    conn.commit()
    conn.close()

def load_stall(path="STALL.txt"):
    conn = sqlite3.connect(DB)

    with open(path, "r") as f: #closes automatically
        next(f) #skips header
        for line in f:
            line = line.strip()
            if not line: 
                continue
            stallID_str, stallName = [x.strip() for x in line.split(",", 1)]
            if stallID_str:
                conn.execute(
                    "INSERT OR INTO stall(stallID, stallName) VALUES(?, ?)",
                    (int(stallID_str), stallName),
                )
            else:
                conn.execute("INSERT INTO stall(stallName) VALUES(?)",(stallName,))
    
conn.commit()
    conn.close()

def load_dish(path="DISH.txt"):
    conn = sqlite3.connect(DB)

    with open(path, "r") as f: #closes automatically
        next(f) #skips header
        for line in f:
            line = line.strip()
            if not line: 
                continue
            dishID, stallID, dishName, price, availability = [x.strip() for x in line.split(",")]
            conn.execute(
                "INSERT INTO dish(dishID, stallID, dishName, price, availability) VALUES(?,?,?,?,?)",
                (int(dishID), int(stallID), dishName, float(price), availability),
            )

    conn.commit()
    conn.close()

def load_orderdish(path="ORDERDISH.txt"):
    conn = sqlite3.connect(DB)

    with open(path, "r") as f: #closes automatically
        next(f) #skips header
        for line in f:
            line = line.strip()
            if not line: 
                continue
            studentID, dishID, orderDate, orderTime, qty = [x.strip() for x in line.split(",")]
            conn.execute(
                "INSERT INTO orderDish(studentID, dishID, orderTime, orderDate, quantity) VALUES(?,?,?,?,?)",
                (studentID, int(dishID), orderTime, orderDate, int(qty)),
            )

    conn.commit()
    conn.close()

load_student()
load_stall()
load_dish()
load_orderdish()

print("Data import complete.")
