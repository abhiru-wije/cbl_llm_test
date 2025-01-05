import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = OpenAI(api_key=OPENAI_API_KEY)
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]

SYSTEM = """You are an expert email classification agent at Ceylon Biscuit Limited with specialized knowledge of internal business communication. Your task is to analyze emails classified as non-marketing and assign them to one of the following categories: ["HR Emails", "Calendar Invites", "SharePoint Notifications", "Internal Communication", "Transactional Emails", "Custom Email"].

To perform this task accurately, you will evaluate the email address, subject line, and content of the email. Use your deep analytical understanding of email content and context to determine the correct category:

    1. HR Emails: Emails related to human resources, such as recruitment, employee benefits, company policies, or official HR announcements.
    2. Calendar Invites: Emails that are meeting invitations or event notifications.
    3. SharePoint Notifications: System-generated emails from SharePoint, such as updates, access notifications, or document sharing.
    4. Internal Communication: Emails meant for general or team communication within the company that do not fall under HR, transactional, or notification types.
    5. Transactional Emails: Emails triggered by a specific action, such as purchase confirmations, system alerts, or automated reports.
    6. Custom Email: Any non-marketing email that does not fit into the above categories.

Your output should strictly be one of the six predefined categories. Use all available details in the email to make an informed decision. Respond only with the category name as your output.
"""

class NonMarketingEmailClassification(BaseModel):
    from_address: str = Field(description="Sender email address")
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")
    created_date: str = Field(description="Email creation date")
    
def classify_non_marketing(from_address: str, to: str, subject: str, body: str, created_date: str) -> str:
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
        
        data = {
            "from_address": from_address,
            "to": to,
            "subject": subject,
            "body": body,
            "created_date": created_date,
            "type": result
        }
        
        collection = db["nonMarketingEmails"]
        query = collection.insert_one(data)
        return {"Emails Classify as": result, "ID": str(query.inserted_id)}
    except Exception as e:
        print("Error: ", e)
        
def non_marketing_classification_executor(args):
    return classify_non_marketing(args["from_address"], args["to"], args["subject"], args["body"], args["created_date"])

non_marketing_classification_tool = {
    "type": "function",
    "function": {
        "name": "classify_non_marketing_email",
        "description": "classify the non marketing emails into different categories",
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