db.students.updateOne(
  { name: "Alice Johnson" },
  { $unset: { address: "" } }
)