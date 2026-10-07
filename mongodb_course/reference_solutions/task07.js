db.students.updateOne(
  { name: "Alice Johnson" },
  { $rename: { name: "fullName" } }
)