import uuid

class Transaction:
    def __init__(self, date, amount, type, category, memo, id=None):
        self.id = id or str(uuid.uuid4())
        self.date = date
        self.amount = amount
        self.type = type 
        self.category = category
        self.memo = memo
