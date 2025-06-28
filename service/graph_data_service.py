from collections import defaultdict
from datetime import datetime

class GraphDataService:
    def __init__(self, transactions):
        self.transactions = transactions

    def get_monthly_data(self):
        monthly_data = defaultdict(lambda: {"수입": 0, "지출": 0})
        for t in self.transactions:
            month = t.date[:7]  # YYYY-MM 형식
            monthly_data[month][t.type] += t.amount
        return dict(monthly_data)

    def get_category_data(self):
        category_data = defaultdict(lambda: defaultdict(int))
        for t in self.transactions:
            if t.type == "지출":
                month = t.date[:7]
                category_data[month][t.category] += t.amount
        return {month: dict(categories) for month, categories in category_data.items()}
