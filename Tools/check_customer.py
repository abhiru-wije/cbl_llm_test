from pydantic import BaseModel, Field
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

class CheckCustomer(BaseModel):
    from_address: str = Field(description="Sender email address")
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")
    created_date: str = Field(description="Email creation date")
    

def check_customer(from_address: str, to: str, subject: str, body: str, created_date: str) -> dict:
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db["emails"]
        
        existing_customer = collection.find_one({"from_address": from_address})
        if existing_customer:
            return {
                "message": "Existing Customer",
                "is_existing_customer": True,
                "customer_id": str(existing_customer["_id"])
            }
        else:
            marketing_collection = db["marketingEmails"]
            
            new_customer = {
                "from_address": from_address,
                "to": to,
                "subject": subject,
                "body": body,
                "created_date": created_date,
                "type": "Lead"
            }
            result = marketing_collection.insert_one(new_customer)
            
            return {
                "message": "New Customer",
                "is_existing_customer": False,
                "customer_id": str(result.inserted_id)
            }
    except Exception as e:
        return str(e)
    
def check_customer_executor(args):
    return check_customer(args["from_address"])

check_customer_tool = {
    "type": "function",
    "function": {
        "name": "check_customer",
        "description": "Check if a customer exists in the database",
        "parameters": {
            "type": "object",
            "properties": {
                "from_address" : {
                    "type" : "string",
                    "description"  : "Sender email address"
                },
                "to":{
                    "type" : "string",
                    "description" : "Recipient email address"
                },
                "subject":{
                    "type" : "string",
                    "description" : "Email subject"
                },
                "body":{
                    "type" : "string",
                    "description" : "Email body"
                },
                "created_date":{
                    "type" : "string",
                    "description" : "Email creation date"
                }
            },
            "required": ["from_address", "to", "subject", "body", "created_date"]
        }
    }
}