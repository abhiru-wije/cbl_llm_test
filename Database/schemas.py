import datetime

class Email:
    def __init__(self, data):
        if data is None:
            self._id = None
            self.to_address = None
            self.from_address = None
            self.subject = None
            self.body = None
            self.created_date = None
        else:
            self._id = data.get('_id')
            self.to_address = data.get('to_address')
            self.from_address = data.get('from_address')
            self.subject = data.get('subject')
            self.body = data.get('body')
            self.created_date = data.get('created_date')
            
    def to_dict(self):
        return {
            '_id': self._id,
            'to_address': self.to_address,
            'from_address': self.from_address,
            'subject': self.subject,
            'body': self.body,
            'created_date': self.created_date
        }

class User:
    def __init__(self, data):
        if data is None:
            self._id = None
            self.email = None
        else:
            self._id = data.get('_id')
            self.email = data.get('email')
            
    def to_dict(self):
        return {
            '_id': self._id,
            'email': self.email
        }
    
            