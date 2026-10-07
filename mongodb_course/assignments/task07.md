# Task 07: Rename Field

## Description
Rename the field `name` to `fullName` in the student document for "Alice Johnson".

## Collections
- students

## Expected Result
After the update, the document for Alice Johnson should have a field `fullName` with value "Alice Johnson", and the field `name` should no longer exist.

## Example Solution
```javascript
db.students.updateOne(
  { name: "Alice Johnson" },
  { $rename: { name: "fullName" } }
)
```