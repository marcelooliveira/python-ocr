import os
from pymongo import MongoClient

class MongoDBHelper:
    def __init__(self):
        connection_string = os.environ["MONGO_DB_CONNECTION_STRING"]
        db = os.environ["MONGO_DB_NAME"]
        collection = os.environ["MONGO_COLLECTION_ID"]
        self.client = MongoClient(connection_string)
        self.db = self.client[db]
        self.collection = self.db[collection]

    def create_document(self, document):
        result = self.collection.insert_one(document)
        return result.inserted_id

    def read_document(self, query):
        document = self.collection.find_one(query)
        return document

    def update_document(self, query, update_data):
        result = self.collection.update_one(query, {"$set": update_data})
        return result.modified_count

    def delete_document(self, query):
        result = self.collection.delete_one(query)
        return result.deleted_count


# Usage example
if __name__ == "__main__":
    connection_string = os.environ["MONGO_DB_CONNECTION_STRING"]
    db_name = os.environ["MONGO_DB_NAME"]
    collection_name = os.environ["MONGO_COLLECTION_ID"]

    db_helper = MongoDBHelper(connection_string, db_name, collection_name)

    # Create a document
    new_document = {
        "title": "Sample Document",
        "content": "This is a sample document."
    }
    inserted_id = db_helper.create_document(new_document)
    print("Inserted document ID:", inserted_id)

    # Read a document
    query = {"title": "Sample Document"}
    retrieved_document = db_helper.read_document(query)
    print("Retrieved document:", retrieved_document)

    # Update a document
    update_query = {"title": "Sample Document"}
    update_data = {"content": "Updated content"}
    modified_count = db_helper.update_document(update_query, update_data)
    print("Modified document count:", modified_count)

    # Delete a document
    delete_query = {"title": "Sample Document"}
    deleted_count = db_helper.delete_document(delete_query)
    print("Deleted document count:", deleted_count)
