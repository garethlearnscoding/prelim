SELECT SUM(Equipment.Points) FROM Equipment, Loan, Student
WHERE Equipment.ID = Loan.EquipmentID
AND Loan.StudentID = Student.ID
AND Student.Name = 'Andy';


SELECT Student.Name, SUM(Equipment.Points)
FROM Loan, Equipment, Student
WHERE Loan.EquipmentID = Equipment.ID
AND Student.ID = Loan.StudentID
GROUP by Student.Name
ORDER by SUM(Equipment.Points) DESC
LIMIT 3;
