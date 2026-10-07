# Task 05: Update multiple documents

## Description
Increment the age of all students majoring in "Computer Science" by 1.

## Collections
- students

## Expected Result
After the update, the students with major "Computer Science" (Alice Johnson and David Brown) should have their age increased by 1.
Alice Johnson: originally 20 -> 21
David Brown: originally 23 -> 24

## Example Solution
```javascript
db.students.updateMany(
  { major: "Computer Science" },
  { $inc: { age: 1 } }
)
```