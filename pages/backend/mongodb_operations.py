import os
import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class MongoDBHandler:
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(self.uri)
        self.db_name = os.getenv("MONGODB_DB_NAME", "rag_db")
        self.collection_name = os.getenv("MONGODB_COLLECTION_NAME", "chat_history")
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def insert_chat_message(self, role, message):
        """Insert a chat message into the collection."""
        document = {
            "role": role,
            "message": message,
            "timestamp": datetime.datetime.now()
        }
        self.collection.insert_one(document)

    def get_chat_history(self, limit=100):
        """Retrieve chat history from the collection, sorted by timestamp (oldest first), returning only role and message."""
        cursor = self.collection.find().sort("timestamp", 1).limit(limit)
        return [{"role": doc["role"], "message": doc["message"]} for doc in cursor]

    def clear_chat_history(self):
        """Clear all chat messages from the collection."""
        self.collection.delete_many({})

    def close_connection(self):
        """Close the MongoDB connection."""
        self.client.close()

# Example usage (for testing)
if __name__ == "__main__":
    db_handler = MongoDBHandler()
    db_handler.insert_chat_message("user", "Hello, world!")
    db_handler.insert_chat_message("assistant", "Hi there!")
    history = db_handler.get_chat_history()
    for msg in history:
        print(f"{msg['role']}: {msg['message']}")
    db_handler.close_connection()