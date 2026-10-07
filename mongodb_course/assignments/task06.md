# Task 06: Unset Field

## Description
Remove the address field from the student named "Alice Johnson".

## Collections
- students

## Expected Result
After the update, the document for Alice Johnson should no longer have the address field.

## Example Solution
```javascript
db.students.updateOne(
  { name: "Alice Johnson" },
  { $unset: { address: "" } }
)
```