class Transaction:
    def __init__(self, date, amount, type_, category, memo):
        self.date = date
        self.amount = amount
        self.type = type_  # "수입" 또는 "지출"
        self.category = category
        self.memo = memo