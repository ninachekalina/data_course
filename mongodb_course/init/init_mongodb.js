// MongoDB initialization script for educational course
// This script creates the mongodb_course database and populates it with sample data

print("Initializing mongodb_course database...");

// Connect to the MongoDB instance
// In Docker/CI environment, this will connect to localhost:27017
db = db.getSiblingDB("mongodb_course");

// Drop the database if it exists to start fresh
print("Dropping existing mongodb_course database...");
db.dropDatabase();

// Create collections
print("Creating collections...");
db.createCollection("students");
db.createCollection("courses");
db.createCollection("teachers");
db.createCollection("enrollments");
db.createCollection("assignments");
db.createCollection("results");

// Load data from JSON files
print("Loading data...");

// Load students
var students = [
  {
    "_id": "507f1f77bcf86cd799439011",
    "name": "Alice Johnson",
    "age": 20,
    "major": "Computer Science",
    "address": {
      "street": "123 Main St",
      "city": "Seattle",
      "zip": "98101"
    }
  },
  {
    "_id": "507f1f77bcf86cd799439012",
    "name": "Bob Smith",
    "age": 22,
    "major": "Mathematics",
    "address": {
      "street": "456 Oak Ave",
      "city": "Boston",
      "zip": "02101"
    }
  },
  {
    "_id": "507f1f77bcf86cd799439013",
    "name": "Carol Williams",
    "age": 21,
    "major": "Physics",
    "address": {
      "street": "789 Pine Rd",
      "city": "Austin",
      "zip": "78701"
    }
  },
  {
    "_id": "507f1f77bcf86cd799439014",
    "name": "David Brown",
    "age": 23,
    "major": "Computer Science",
    "address": {
      "street": "321 Elm St",
      "city": "New York",
      "zip": "10001"
    }
  },
  {
    "_id": "507f1f77bcf86cd799439015",
    "name": "Eva Davis",
    "age": 20,
    "major": "Biology",
    "address": {
      "street": "654 Maple Dr",
      "city": "Chicago",
      "zip": "60601"
    }
  }
];
db.students.insertMany(students);

// Load courses
var courses = [
  {
    "_id": "CSC101",
    "name": "Introduction to Computer Science",
    "credits": 3,
    "department": "Computer Science",
    "instructor_id": "T001",
    "schedule": {
      "days": ["Monday", "Wednesday"],
      "time": "10:00-11:30"
    }
  },
  {
    "_id": "MAT201",
    "name": "Calculus II",
    "credits": 4,
    "department": "Mathematics",
    "instructor_id": "T002",
    "schedule": {
      "days": ["Tuesday", "Thursday"],
      "time": "14:00-15:30"
    }
  },
  {
    "_id": "PHY101",
    "name": "General Physics I",
    "credits": 3,
    "department": "Physics",
    "instructor_id": "T003",
    "schedule": {
      "days": ["Monday", "Wednesday", "Friday"],
      "time": "09:00-10:00"
    }
  },
  {
    "_id": "BIO301",
    "name": "Molecular Biology",
    "credits": 4,
    "department": "Biology",
    "instructor_id": "T004",
    "schedule": {
      "days": ["Tuesday", "Thursday"],
      "time": "11:00-12:30"
    }
  },
  {
    "_id": "ENG101",
    "name": "English Composition",
    "credits": 3,
    "department": "English",
    "instructor_id": "T005",
    "schedule": {
      "days": ["Monday", "Wednesday"],
      "time": "13:00-14:30"
    }
  }
];
db.courses.insertMany(courses);

// Load teachers
var teachers = [
  {
    "_id": "T001",
    "name": "Dr. John Smith",
    "department": "Computer Science",
    "title": "Associate Professor",
    "email": "john.smith@university.edu",
    "office": "CS Building, Room 301"
  },
  {
    "_id": "T002",
    "name": "Dr. Maria Garcia",
    "department": "Mathematics",
    "title": "Professor",
    "email": "maria.garcia@university.edu",
    "office": "Math Building, Room 205"
  },
  {
    "_id": "T003",
    "name": "Dr. Robert Chen",
    "department": "Physics",
    "title": "Assistant Professor",
    "email": "robert.chen@university.edu",
    "office": "Physics Building, Room 108"
  },
  {
    "_id": "T004",
    "name": "Dr. Lisa Wang",
    "department": "Biology",
    "title": "Associate Professor",
    "email": "lisa.wang@university.edu",
    "office": "Bio Building, Room 402"
  },
  {
    "_id": "T005",
    "name": "Dr. James Wilson",
    "department": "English",
    "title": "Professor",
    "email": "james.wilson@university.edu",
    "office": "Liberal Arts, Room 150"
  }
];
db.teachers.insertMany(teachers);

// Load enrollments
var enrollments = [
  {
    "student_id": "507f1f77bcf86cd799439011",
    "course_id": "CSC101",
    "enrollment_date": "2023-09-01"
  },
  {
    "student_id": "507f1f77bcf86cd799439011",
    "course_id": "MAT201",
    "enrollment_date": "2023-09-01"
  },
  {
    "student_id": "507f1f77bcf86cd799439012",
    "course_id": "MAT201",
    "enrollment_date": "2023-09-01"
  },
  {
    "student_id": "507f1f77bcf86cd799439012",
    "course_id": "PHY101",
    "enrollment_date": "2023-09-01"
  },
  {
    "student_id": "507f1f77bcf86cd799439013",
    "course_id": "PHY101",
    "enrollment_date": "2023-09-01"
  },
  {
    "student_id": "507f1f77bcf86cd799439013",
    "course_id": "BIO301",
    "enrollment_date": "2023-09-01"
  },
  {
    "student_id": "507f1f77bcf86cd799439014",
    "course_id": "BIO301",
    "enrollment_date": "2023-09-01"
  },
  {
    "student_id": "507f1f77bcf86cd799439014",
    "course_id": "ENG101",
    "enrollment_date": "2023-09-01"
  },
  {
    "student_id": "507f1f77bcf86cd799439015",
    "course_id": "ENG101",
    "enrollment_date": "2023-09-01"
  },
  {
    "student_id": "507f1f77bcf86cd799439015",
    "course_id": "CSC101",
    "enrollment_date": "2023-09-01"
  }
];
db.enrollments.insertMany(enrollments);

// Create sample assignments
var assignments = [
  {
    "_id": "A001",
    "course_id": "CSC101",
    "title": "Introduction to Python",
    "description": "Basic Python programming assignment",
    "due_date": "2023-10-15",
    "max_points": 100
  },
  {
    "_id": "A002",
    "course_id": "MAT201",
    "title": "Integration Techniques",
    "description": "Practice integration problems",
    "due_date": "2023-10-20",
    "max_points": 100
  },
  {
    "_id": "A003",
    "course_id": "PHY101",
    "title": "Kinematics Problems",
    "description": "Solve motion problems",
    "due_date": "2023-10-18",
    "max_points": 100
  }
];
db.assignments.insertMany(assignments);

// Create sample results
var results = [
  {
    "student_id": "507f1f77bcf86cd799439011",
    "assignment_id": "A001",
    "score": 85,
    "submitted_date": "2023-10-10"
  },
  {
    "student_id": "507f1f77bcf86cd799439012",
    "assignment_id": "A001",
    "score": 92,
    "submitted_date": "2023-10-12"
  },
  {
    "student_id": "507f1f77bcf86cd799439013",
    "assignment_id": "A002",
    "score": 78,
    "submitted_date": "2023-10-15"
  }
];
db.results.insertMany(results);

// Create indexes for better query performance
print("Creating indexes...");
db.students.createIndex({ "name": 1 });
db.students.createIndex({ "age": 1 });
db.students.createIndex({ "major": 1 });
db.courses.createIndex({ "department": 1 });
db.courses.createIndex({ "credits": 1 });
db.teachers.createIndex({ "department": 1 });
db.enrollments.createIndex({ "student_id": 1 });
db.enrollments.createIndex({ "course_id": 1 });
db.assignments.createIndex({ "course_id": 1 });
db.results.createIndex({ "student_id": 1 });
db.results.createIndex({ "assignment_id": 1 });

// Verify data was loaded
print("Data loaded successfully:");
print("Students: " + db.students.countDocuments());
print("Courses: " + db.courses.countDocuments());
print("Teachers: " + db.teachers.countDocuments());
print("Enrollments: " + db.enrollments.countDocuments());
print("Assignments: " + db.assignments.countDocuments());
print("Results: " + db.results.countDocuments());

print("mongodb_course database initialization complete!");