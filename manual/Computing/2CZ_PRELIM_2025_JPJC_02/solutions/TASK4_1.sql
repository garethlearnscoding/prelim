CREATE TABLE IF NOT EXISTS student (
  studentID   TEXT PRIMARY KEY,    
  name        TEXT NOT NULL,
  phoneNo     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stall (
  stallID     INTEGER PRIMARY KEY AUTOINCREMENT,
  stallName   TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dish (
  dishID      INTEGER PRIMARY KEY AUTOINCREMENT,
  stallID     INTEGER NOT NULL,
  dishName    TEXT NOT NULL,
  price       REAL NOT NULL CHECK (price >= 0),
  availability TEXT NOT NULL,
  FOREIGN KEY (stallID) REFERENCES stall(stallID) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS orderDish (
  studentID   TEXT    NOT NULL,
  dishID      INTEGER NOT NULL,
  orderTime   TEXT    NOT NULL,   
  orderDate   TEXT    NOT NULL,   
  quantity    INTEGER NOT NULL CHECK (quantity > 0),
  PRIMARY KEY (studentID, dishID, orderTime, orderDate),
  FOREIGN KEY (studentID) REFERENCES student(studentID) ON UPDATE CASCADE ON DELETE CASCADE,
  FOREIGN KEY (dishID)    REFERENCES dish(dishID) ON UPDATE CASCADE ON DELETE CASCADE
);
