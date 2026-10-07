# Task 01: Find all students

## Description
Find all documents in the students collection and return all fields.

## Collections
- students

## Expected Result
Should return all 5 student documents with all fields including _id, name, age, major, and address.

## Example Solution
```javascript
db.students.find()
```