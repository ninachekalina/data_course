db.students.updateOne(
  { name: "Alice Johnson" },
  { $set: { age: 21 } }
)