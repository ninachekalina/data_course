const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');
const assert = require('assert');

describe('Task 02: Find students older than 21', function() {
    let client;
    let db;

    before(async function() {
        client = new MongoClient('mongodb://localhost:27017');
        await client.connect();
        db = client.db('mongodb_course');

        // Reset the database by dropping and recreating with seed data
        await db.dropDatabase();

        // Insert seed data from JSON files
        const studentsData = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'students.json'), 'utf8'));
        await db.collection('students').insertMany(studentsData);

        const coursesData = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'courses.json'), 'utf8'));
        await db.collection('courses').insertMany(coursesData);

        const teachersData = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'teachers.json'), 'utf8'));
        await db.collection('teachers').insertMany(teachersData);

        const enrollmentsData = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'enrollments.json'), 'utf8'));
        await db.collection('enrollments').insertMany(enrollmentsData);

        const assignmentsData = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'assignments.json'), 'utf8'));
        await db.collection('assignments').insertMany(assignmentsData);

        const resultsData = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'results.json'), 'utf8'));
        await db.collection('results').insertMany(resultsData);

        // Create indexes
        await db.collection('students').createIndex({ "name": 1 });
        await db.collection('students').createIndex({ "age": 1 });
        await db.collection('students').createIndex({ "major": 1 });
        await db.collection('courses').createIndex({ "department": 1 });
        await db.collection('courses').createIndex({ "credits": 1 });
        await db.collection('teachers').createIndex({ "department": 1 });
        await db.collection('enrollments').createIndex({ "student_id": 1 });
        await db.collection('enrollments').createIndex({ "course_id": 1 });
        await db.collection('assignments').createIndex({ "course_id": 1 });
        await db.collection('results').createIndex({ "student_id": 1 });
        await db.collection('results').createIndex({ "assignment_id": 1 });
    });

    after(async function() {
        await client.close();
    });

    it('should return students older than 21', async function() {
        // Read the student's solution
        const solutionPath = path.join(__dirname, '..', 'solutions', 'task02.js');
        let studentCode;
        try {
            studentCode = fs.readFileSync(solutionPath, 'utf8');
        } catch (e) {
            throw new Error(`Could not read solution file at ${solutionPath}: ${e.message}`);
        }

        // Prepare db object with collections attached for the student's code
        const dbWithCollections = db;
        dbWithCollections.students = db.collection('students');
        dbWithCollections.courses = db.collection('courses');
        dbWithCollections.teachers = db.collection('teachers');
        dbWithCollections.enrollments = db.collection('enrollments');
        dbWithCollections.assignments = db.collection('assignments');
        dbWithCollections.results = db.collection('results');

        // Execute student's solution
        let result;
        try {
            // Use vm to run the code in a context
            const vm = require('vm');
            const context = { db: dbWithCollections };
            const script = new vm.Script(studentCode);
            result = script.runInContext(context);
        } catch (e) {
            throw new Error(`Error executing student's solution: ${e.message}`);
        }

        // If result is a cursor, convert to array
        if (result && typeof result === 'object' && typeof result.toArray === 'function') {
            result = await result.toArray();
        }

        // Get expected result from database
        const expected = await db.collection('students').find({ age: { $gt: 21 } }).toArray();

        // Sort both arrays by _id for consistent comparison
        const sortById = (a, b) => a._id < b._id ? -1 : 1;
        const sortedResult = result.slice().sort(sortById);
        const sortedExpected = expected.slice().sort(sortById);

        // Deep equality check
        assert.deepStrictEqual(sortedResult, sortedExpected);
    });
});