import os
import datetime
from Database.schemas import Email, User
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv('DB_NAME')

class DBService:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DBService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'is_initialized'):
            self.client = MongoClient(os.getenv('MONGO_URI'))
            
            #database
            self.db = self.client[DB_NAME]

            #collections
            self.emails = self.db['emails']
            self.users = self.db['users']
            self.marketing_emails = self.db['marketingEmails']
            self.non_marketing_emails = self.db['nonMarketingEmails']
            