# Task 04: Update a student's age

## Description
Update the age of the student named "Alice Johnson" to 21.

## Collections
- students

## Expected Result
After the update, the student document for Alice Johnson should have age: 21.

## Example Solution
```javascript
db.students.updateOne(
  { name: "Alice Johnson" },
  { $set: { age: 21 } }
)
```