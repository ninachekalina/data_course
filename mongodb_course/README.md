# MongoDB Educational Course

This repository contains a series of MongoDB assignments and automated tests for educational purposes.

## Structure

- `assignments/`: Markdown files describing each task.
- `solutions/`: Example solutions for each task (JavaScript files).
- `tests/`: Test files that validate student solutions.
- `data/`: Seed data in JSON format for the MongoDB database.

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- MongoDB (v4.4 or higher) running locally on port 27017

### Installation

1. Clone the repository.
2. Navigate to the `mongodb_course` directory.
3. Install dependencies:

```bash
npm install
```

### Running Tests Locally

Ensure MongoDB is running on `localhost:27017`, then run:

```bash
npm test
```

This will execute the test suite and report which tasks pass or fail.

### GitHub Actions

The repository includes a GitHub Actions workflow (`.github/workflows/mongodb-course.yml`) that runs the tests on every push and pull request. The workflow uses a MongoDB Docker service to provide the database.

## Task List

Each task is independent and includes:
- A description in `assignments/taskXX.md`
- An example solution in `solutions/taskXX.js`
- A test in `tests/test_taskXX.js`

The tasks cover:
- Basic find operations
- Queries with conditions
- Projection
- Update operations (updateOne, updateMany)
- Unset fields
- Rename fields
- And more advanced operations (aggregation, indexing, etc.)

## How to Use

Students should:
1. Read the assignment description.
2. Write their solution in a JavaScript file (or directly in the MongoDB shell).
3. Push their solution to their fork of the repository.
4. The GitHub Actions workflow will automatically test their solution and report the results.

Alternatively, they can run the tests locally before pushing.

## License

This project is for educational use.