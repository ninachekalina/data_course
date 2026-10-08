const { MongoClient } = require('mongodb');
const fs = require('fs');
const path = require('path');

async function runTests() {
    console.log('MongoDB Course - Automated Test Suite');
    console.log('====================================');

    const client = new MongoClient('mongodb://localhost:27017');
    let passed = 0;
    let total = 0;

    try {
        await client.connect();
        const db = client.db('mongodb_course');

        // Determine solutions directory from environment variable, default to 'solutions'
        const solutionsDir = process.env.TEST_SOLUTIONS_DIR || path.join(__dirname, '..', 'solutions');

        // Find all test files
        const testDir = path.join(__dirname);
        const files = fs.readdirSync(testDir);
        const testFiles = files.filter(file => file.startsWith('test_task') && file.endsWith('.js'));

        // Sort test files numerically
        testFiles.sort((a, b) => {
            const numA = parseInt(a.match(/task(\d+)/)[1]);
            const numB = parseInt(b.match(/task(\d+)/)[1]);
            return numA - numB;
        });

        for (const testFile of testFiles) {
            total++;
            const taskNum = testFile.match(/task(\d+)/)[1];
            console.log(`\nTask ${taskNum}:`);

            try {
                // Reset database for each test
                await db.dropDatabase();

                // Insert seed data
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

                // Create indexes (matching what's in the individual test files)
                await db.collection('students').createIndex({ "name": 1 });
                await db.collection('students').createIndex({ "age": 1 });
                await db.collection('students').createIndex({ "major": 1 });

                // Read the student's solution
                const solutionPath = path.join(solutionsDir, `task${taskNum}.js`);
                let studentCode;
                try {
                    studentCode = fs.readFileSync(solutionPath, 'utf8');
                } catch (e) {
                    console.log(`  NOT SUBMITTED - Solution file not found: ${solutionPath}`);
                    // Skip to next test
                    continue;
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
                    vm.createContext(context); // Make sure the context is properly initialized
                    const script = new vm.Script(studentCode);
                    result = script.runInContext(context);
                    // If the result is a Promise, await it
                    if (result && typeof result.then === 'function') {
                        result = await result;
                    }
                } catch (e) {
                    throw new Error(`Error executing student's solution: ${e.message}`);
                }

                // Convert cursor to array if needed
                if (result && typeof result === 'object' && typeof result.toArray === 'function') {
                    result = await result.toArray();
                }

                // Get expected result based on task
                let expected;
                let isUpdateTask = false;

                switch (parseInt(taskNum)) {
                    case 1:
                        expected = await db.collection('students').find().toArray();
                        break;
                    case 2:
                        expected = await db.collection('students').find({ age: { $gt: 21 } }).toArray();
                        break;
                    case 3:
                        expected = await db.collection('students').find({}, { name: 1, age: 1 }).toArray();
                        break;
                    case 4:
                        // For update task, we need to check the updated document
                        isUpdateTask = true;
                        expected = await db.collection('students').findOne({ name: "Alice Johnson" });
                        // Expected: Alice Johnson's age should be 21
                        break;
                    case 5:
                        // For updateMany task
                        isUpdateTask = true;
                        // Expected: Alice Johnson's age should be 21, David Brown's age should be 24
                        break;
                    case 6:
                        // For unset task
                        isUpdateTask = true;
                        // Expected: Alice Johnson's address field should be undefined
                        break;
                    case 7:
                        // For rename task
                        isUpdateTask = true;
                        // Expected: Alice Johnson should have fullName field with value "Alice Johnson", and no name field
                        break;
                    default:
                        expected = await db.collection('students').find().toArray();
                }

                // Check result
                if (isUpdateTask) {
                    // For update tasks, check the database state directly
                    let passedTask = false;
                    switch (parseInt(taskNum)) {
                        case 4:
                            const aliceAfterTask4 = await db.collection('students').findOne({ name: "Alice Johnson" });
                            if (aliceAfterTask4 && aliceAfterTask4.age === 21) {
                                passedTask = true;
                            } else {
                                console.log(`  FAIL - Expected Alice Johnson's age to be 21, got ${aliceAfterTask4 ? aliceAfterTask4.age : 'null'}`);
                            }
                            break;
                        case 5:
                            const aliceAfterTask5 = await db.collection('students').findOne({ name: "Alice Johnson" });
                            const davidAfterTask5 = await db.collection('students').findOne({ name: "David Brown" });
                            if (aliceAfterTask5 && aliceAfterTask5.age === 21 &&
                                davidAfterTask5 && davidAfterTask5.age === 24) {
                                passedTask = true;
                            } else {
                                console.log(`  FAIL - Expected Alice: 21 (got ${aliceAfterTask5 ? aliceAfterTask5.age : 'null'}), David: 24 (got ${davidAfterTask5 ? davidAfterTask5.age : 'null'})`);
                            }
                            break;
                        case 6:
                            const aliceAfterTask6 = await db.collection('students').findOne({ name: "Alice Johnson" });
                            if (aliceAfterTask6 && aliceAfterTask6.address === undefined) {
                                passedTask = true;
                            } else {
                                console.log(`  FAIL - Expected Alice Johnson's address to be unset, got ${aliceAfterTask6 ? JSON.stringify(aliceAfterTask6.address) : 'null'}`);
                            }
                            break;
                        case 7:
                            const aliceAfterTask7 = await db.collection('students').findOne({ fullName: "Alice Johnson" });
                            if (aliceAfterTask7 && aliceAfterTask7.fullName === "Alice Johnson" && aliceAfterTask7.name === undefined) {
                                passedTask = true;
                            } else {
                                console.log(`  FAIL - Expected Alice Johnson's name to be renamed to fullName, got fullName: ${aliceAfterTask7 ? aliceAfterTask7.fullName : 'null'}, name: ${aliceAfterTask7 ? aliceAfterTask7.name : 'still exists'}`);
                            }
                            break;
                        default:
                            console.log(`  FAIL - Unknown update task`);
                            break;
                    }

                    if (passedTask) {
                        console.log(`  PASS`);
                        passed++;
                    }
                } else {
                    // For find/projection tasks, compare arrays
                    if (Array.isArray(expected) && Array.isArray(result)) {
                        // Sort by _id for consistent comparison
                        const sortById = (a, b) => {
                            if (a._id < b._id) return -1;
                            if (a._id > b._id) return 1;
                            return 0;
                        };

                        const sortedResult = [...result].sort(sortById);
                        const sortedExpected = [...expected].sort(sortById);

                        // Deep equality check
                        const isEqual = JSON.stringify(sortedResult) === JSON.stringify(sortedExpected);

                        if (isEqual) {
                            console.log(`  PASS`);
                            passed++;
                        } else {
                            console.log(`  FAIL - Result mismatch`);
                            console.log(`    Expected length: ${sortedExpected.length}`);
                            console.log(`    Received length: ${sortedResult.length}`);
                        }
                    } else {
                        console.log(`  FAIL - Unexpected result type`);
                    }
                }
            } catch (error) {
                console.log(`  FAIL - ${error.message}`);
            }
        }

        console.log(`\n====================================`);
        console.log(`Score: ${passed}/${total}`);
        console.log(`====================================`);

        if (passed === total) {
            console.log('All tests passed! 🎉');
            return true;
        } else {
            console.log('Some tests failed. Please review your solutions.');
            return false;
        }
    } finally {
        await client.close();
    }
}

// Run tests if this file is executed directly
if (require.main === module) {
    runTests().then(success => {
        process.exit(success ? 0 : 1);
    }).catch(err => {
        console.error('Test runner failed:', err);
        process.exit(1);
    });
}

module.exports = { runTests };