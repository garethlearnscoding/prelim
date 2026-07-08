/*2 marks - For querying students with more than 2 latecoming*/
SELECT Name, Class, Count(*) 
FROM Student
INNER JOIN Latecoming ON Student.StudentID = Latecoming.StudentID /*1 mark for correct inner join */
GROUP BY Name
HAVING Count(*) > 2
ORDER BY Count(*) DESC; /*1 mark for correct group by, having and order by */

/*2 marks - For querying the number of latecoming in each class*/
SELECT Class, Count(*) 
FROM Student
INNER JOIN Latecoming ON Student.StudentID = Latecoming.StudentID /*1 mark for correct inner join */
GROUP BY Class
ORDER BY CLass; /*1 mark for correct group by and order by */