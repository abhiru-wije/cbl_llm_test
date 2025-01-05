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

SYSTEM =  """
You are an expert email classification agent at Ceylon Biscuit Limited specializing in customer communications analysis. Your task is to analyze marketing emails from existing customers and categorize them into one of these types: ["Lead", "Opportunity", "Case", "Complement", "Other"].

Analyze the email subject and body to determine the correct category based on these criteria:

1. Lead: Initial inquiries about products/services, requesting information or pricing
2. Opportunity: Emails indicating purchasing interest, price negotiations, or specific order discussions
3. Case: Customer support requests, complaints, or issues requiring resolution
4. Complement: Positive feedback, testimonials, or appreciation messages
5. Other: Any marketing-related customer email that doesn't fit the above categories

Rules:
- Use only email subject and body content for classification
- Output must be exactly one of the five category names
- No additional text or explanations in output
- Category names are case-sensitive
"""

class MarketingEmailClassification(BaseModel):
    from_address: str = Field(description="Sender email address")
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")
    created_date: str = Field(description="Email creation date")

def classify_marketing(from_address: str, to: str, subject: str, body: str, created_date: str) -> str:
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
        collection = db["marketingEmails"]
        query = collection.insert_one(data)
        return {"Marketing Emails Classify as": result, "ID": str(query.inserted_id)}
    except Exception as e:
        print("Error: ", e)

def marketing_classification_executor(args):
    return classify_marketing(args["from_address"], args["to"], args["subject"], args["body"], args["created_date"])

marketing_classification_tool = {
    "type": "function",
    "function": {
        "name": "classify_marketing_email",
        "description": "classify the marketing emails into different categories",
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
        