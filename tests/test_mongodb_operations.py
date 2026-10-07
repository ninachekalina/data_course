import os
import pytest
from pages.backend.mongodb_operations import MongoDBHandler

def test_mongodb_operations():
    # Set environment variables for test database
    os.environ["MONGODB_URI"] = "mongodb://localhost:27017/"
    os.environ["MONGODB_DB_NAME"] = "rag_db_test"
    os.environ["MONGODB_COLLECTION_NAME"] = "chat_history_test"

    try:
        db_handler = MongoDBHandler()
        # Try to ping the database to see if it's available
        db_handler.client.admin.command('ping')
    except Exception:
        pytest.skip("MongoDB is not available")

    # Clear any existing data in the test collection
    db_handler.clear_chat_history()

    # Test inserting a message
    db_handler.insert_chat_message("user", "Test message")
    db_handler.insert_chat_message("assistant", "Test response")

    # Test retrieving chat history
    history = db_handler.get_chat_history(limit=10)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["message"] == "Test message"
    assert history[1]["role"] == "assistant"
    assert history[1]["message"] == "Test response"

    # Test clearing chat history
    db_handler.clear_chat_history()
    history_after_clear = db_handler.get_chat_history(limit=10)
    assert len(history_after_clear) == 0

    # Close connection
    db_handler.close_connection()

    # Drop the test database
    client = MongoDBHandler().client
    client.drop_database(os.environ["MONGODB_DB_NAME"])
    client.close()