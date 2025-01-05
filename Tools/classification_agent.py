import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# MONGO_URI = os.getenv("MONGO_URI")
# DB_NAME = os.getenv("DB_NAME")

client = OpenAI(api_key=OPENAI_API_KEY)
# mongo_client = MongoClient(MONGO_URI)
# db = mongo_client[DB_NAME]

SYSTEM =  """
You are an expert agent at classfying emails into categories at ceylon buiscuit limited. Your task is to look at the email address, email subject and email body and classify the email into one of the following categories: 'Marketing', 'Non-Marketing'. \ 
You can use the information provided in the email to make your decision. If the email is promotional, contains offers, discounts, or sales-related language, categorize it as 'Marketing'. Otherwise, categorize it as 'Non-Marketing'.\
    You have to have deeper level knowledge of the email content to make the right decision. Send the response only as 'Marketing' or 'Non-Marketing' to the user. 
"""

class ClassificationAgent(BaseModel):
    from_address: str = Field(description="Sender email address")
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")
    created_date: str = Field(description="Email creation date")
    
def classify(from_address: str, to: str, subject: str, body: str, created_date: str) -> str:
    input = {
        "from_address": from_address,
        "to": to,
        "subject": subject,
        "body": body,
        "created_date": created_date
    }
    input = json.dumps(input)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": input}],
            temperature=0,
        )
        result = response.choices[0].message.content
        
        # data = {
        #     "from_address": from_address,
        #     "to": to,
        #     "subject": subject,
        #     "body": body,
        #     "created_date": created_date,
        #     "classification": result
        # }
        
        if result == "Marketing":
            # collection = db["marketingEmails"]
            # result = collection.insert_one(data)
            return "Marketing"
        elif result == "Non-Marketing":
            # collection = db["nonMarketingEmails"]
            # result = collection.insert_one(data)
            return "Non-Marketing"
        else:
            return json.dumps({"error": "Email classification failed"})
    except Exception as e:
        return json.dumps({"error": str(e)})

def classify_executor(args):
    return classify(args["from_address"], args["to"], args["subject"], args["body"], args["created_date"])

classify_tool = {
    "type": "function",
    "function": {
        "name": "classify_email_as_marketing_or_non_marketing",
        "description": "Classify the email as marketing or non-marketing",
        "parameters": {
            "type": "object",
            "properties": {
                "from_address": {
                    "type": "string",
                    "description": "Sender email address"
                },
                "to": {
                    "type": "string",
                    "description": "Recipient email address"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject"
                },
                "body": {
                    "type": "string",
                    "description": "Email body"
                },
                "created_date": {
                    "type": "string",
                    "description": "Email creation date"
                }
            },
            "required": ["from_address", "to", "subject", "body", "created_date"]
        }
    }
}