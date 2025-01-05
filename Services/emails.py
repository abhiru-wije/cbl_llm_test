import os
import datetime
from Database.db_service import DBService
from pymongo import MongoClient
from dotenv import load_dotenv
import json
from bson import ObjectId

load_dotenv()
db_service = DBService()    

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = MongoClient(MONGO_URI)
db = db_service.db
email_collection = db_service.emails

def add_new_email(data):
    print("Adding email")
    data["_id"] = ObjectId()
    try:
        collection = email_collection
        result = collection.insert_one(data)
        
        client.close()
        return {"status": "success", "message": "Email added successfully", "id": str(result.inserted_id)}
    except Exception as e:
        print("Error: ", e)
        
def get_emails():
    print("Getting emails")
    
    try:
        collection = email_collection
        emails = list(collection.find())
        
        for email in emails:
            email["_id"] = str(email["_id"])
            
        client.close()
        
        return json.dumps(emails)
    except Exception as e:
        print("Error: ", e)