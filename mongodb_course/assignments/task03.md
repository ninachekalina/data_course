# Task 03: Projection - Name and Age Only

## Description
Find all students but return only the name and age fields (and the _id field which is always included unless explicitly excluded).

## Collections
- students

## Expected Result
Should return 5 documents, each containing only _id, name, and age fields.

## Example Solution
```javascript
db.students.find({}, { name: 1, age: 1 })
```