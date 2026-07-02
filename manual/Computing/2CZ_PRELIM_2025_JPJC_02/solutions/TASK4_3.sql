SELECT d.dishName, d.price
FROM dish AS d
JOIN stall AS s ON s.stallID = d.stallID
WHERE s.stallName = 'Spicy Delight'
  AND d.availability = 'Available'
ORDER BY d.dishName ASC;