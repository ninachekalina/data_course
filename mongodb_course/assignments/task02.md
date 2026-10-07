# Task 02: Find students older than 21

## Description
Find all students who are older than 21 years old.

## Collections
- students

## Expected Result
Should return 2 documents: Bob Smith (age 22) and David Brown (age 23).

## Example Solution
```javascript
db.students.find({ age: { $gt: 21 } })
```