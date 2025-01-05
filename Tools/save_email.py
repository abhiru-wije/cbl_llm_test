from pydantic import BaseModel, Field
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")


class SaveEmail(BaseModel):
    from_address: str = Field(description="Sender email address")
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")
    created_date: str = Field(description="Email creation date")
    
def save_email(from_address: str, to: str, subject: str, body: str, created_date: str) -> str:
    print("Adding email")
    
    data = {
        "from_address": from_address,
        "to": to,
        "subject": subject,
        "body": body,
        "created_date": created_date
    }
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db["emails"]
        
        result = collection.insert_one(data)
        return {"status": "success", "message": "Email added successfully", "id": str(result.inserted_id)}
    except Exception as e:
        print("Error: ", e) 

def save_email_executor(args):
    return save_email(args["from_address"], args["to"], args["subject"], args["body"], args["created_date"])

save_email_tool = {
    "type": "function",
    "function": {
        "name": "save_email",
        "description": "Save an email to the database",
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