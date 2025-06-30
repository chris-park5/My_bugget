from tkinter import messagebox
import os
import json
from collections import defaultdict
from datetime import datetime
from model.transaction import Transaction
from service.graph_data_service import GraphDataService

DATA_DIR = os.path.join(os.path.expanduser("~"), ".my_budget_app")
TRANSACTION_FILE = os.path.join(DATA_DIR, "transactions.json")
GOAL_FILE = os.path.join(DATA_DIR, "goals.json")

class LedgerController:
    def __init__(self, view):
        self.view = view
        self.transactions = []
        self.balance = 0
        self.monthly_goals = {}

        self.view.set_controller(self)
        self.load_data()

    def save_data(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(TRANSACTION_FILE, "w", encoding="utf-8") as f:
            json.dump([t.__dict__ for t in self.transactions], f, ensure_ascii=False, indent=2)
        with open(GOAL_FILE, "w", encoding="utf-8") as f:
            json.dump(self.monthly_goals, f, ensure_ascii=False, indent=2)

    def load_data(self):
        self.transactions.clear()
        self.balance = 0

        if os.path.exists(TRANSACTION_FILE):
            with open(TRANSACTION_FILE, encoding="utf-8") as f:
                for data in json.load(f):
                    if 'type' in data:
                        data['type'] = data.pop('type')
                    t = Transaction(**data)
                    self.transactions.append(t)
                    self.balance += t.amount if t.type == "수입" else -t.amount

        if os.path.exists(GOAL_FILE):
            with open(GOAL_FILE, encoding="utf-8") as f:
                self.monthly_goals = json.load(f)

        monthly_spent = self.calculate_monthly_spent()
        self.view.load_transactions(self.transactions)
        self.view.update_balance(self.balance)
        self.view.load_goals(self.monthly_goals, monthly_spent)
        self.refresh_graph_data()

    def add_transaction(self, date, amount, type_, category, memo):
        try:
            amount = int(amount)
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            self.view.show_error("입력 오류", "날짜는 YYYY-MM-DD 형식, 금액은 숫자여야 합니다.")
            return

        transaction = Transaction(date, amount, type_, category, memo)
        self.transactions.append(transaction)
        self.balance += amount if type_ == "수입" else -amount

        self.view.add_transaction_to_list(transaction, self.balance)
        self.view.update_balance(self.balance)
        self.save_data()

        monthly_spent = self.calculate_monthly_spent()
        self.view.load_goals(self.monthly_goals, monthly_spent)
        self.refresh_graph_data()

    def delete_transaction(self, item_id):
        values = self.view.get_transaction_values(item_id)
        # values: (date, amount, type, category, memo, 잔액)
        target_values = tuple(values[:-1])  # 잔액 제외

        for i, t in enumerate(self.transactions):
            if (t.date, t.amount, t.type, t.category, t.memo) == target_values:
                amount = t.amount
                type_ = t.type
                del self.transactions[i]
                break

        self.balance -= amount if type_ == "수입" else -amount

        self.view.remove_transaction_from_list(item_id)
        self.view.update_balance(self.balance)
        self.save_data()

        monthly_spent = self.calculate_monthly_spent()
        self.view.load_goals(self.monthly_goals, monthly_spent)
        self.refresh_graph_data()
        self.view.load_transactions(self.transactions)
        self.view.update_balance(self.balance)


    def edit_transaction(self, item_id, date, amount, type_, category, memo):
        try:
            amount = int(amount)
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            self.view.show_error("입력 오류", "날짜는 YYYY-MM-DD 형식, 금액은 숫자여야 합니다.")
            return

        old_values = self.view.get_transaction_values(item_id)
        # 잔액 제외하고 비교
        target_values = tuple(old_values[:-1])
        old_amount = int(old_values[1])
        old_type = old_values[2]

        for t in self.transactions:
            if (t.date, t.amount, t.type, t.category, t.memo) == target_values:
                t.date, t.amount, t.type, t.category, t.memo = date, amount, type_, category, memo
                break

        self.balance -= old_amount if old_type == "수입" else -old_amount
        self.balance += amount if type_ == "수입" else -amount

        self.view.update_transaction_in_list(item_id, date, amount, type_, category, memo)
        self.view.update_balance(self.balance)
        self.save_data()

        monthly_spent = self.calculate_monthly_spent()
        self.view.load_goals(self.monthly_goals, monthly_spent)
        self.view.load_transactions(self.transactions)
        self.view.update_balance(self.balance)
        self.refresh_graph_data()

    def set_goal(self, year_month, amount_str):
        try:
            if len(year_month) != 7 or year_month[4] != '-':
                raise ValueError("형식 오류")

            amount = int(amount_str)

            if year_month in self.monthly_goals:
                self.view.show_error("입력 오류", f"{year_month} 목표가 이미 존재합니다. 수정하려면 목표 수정 기능을 사용하세요.")
                return

            self.monthly_goals[year_month] = amount
            self.view.show_info("목표 설정", f"{year_month} 월 목표: {amount}원 저장 완료")

            monthly_spent = self.calculate_monthly_spent()
            self.view.load_goals(self.monthly_goals, monthly_spent)
            self.view.load_transactions(self.transactions)
            self.save_data()
        except Exception as e:
            self.view.show_error("입력 오류",  f"목표 설정 오류: {str(e)}")

    def edit_goal(self, year_month, amount_str):
        try:
            amount = int(amount_str)
            if year_month not in self.monthly_goals:
                self.view.show_error("수정 오류", "선택한 목표가 존재하지 않습니다.")
                return
            self.monthly_goals[year_month] = amount
            self.view.show_info("목표 수정", f"{year_month} 목표가 {amount}원으로 수정되었습니다.")
            monthly_spent = self.calculate_monthly_spent()
            self.view.load_goals(self.monthly_goals, monthly_spent)
            self.view.load_transactions(self.transactions)
            self.save_data()
        except ValueError:
            self.view.show_error("입력 오류", "금액은 숫자여야 합니다.")

    def delete_goal(self, year_month):
        if year_month in self.monthly_goals:
            del self.monthly_goals[year_month]
            self.view.show_info("목표 삭제", f"{year_month} 목표가 삭제되었습니다.")
            monthly_spent = self.calculate_monthly_spent()
            self.view.load_goals(self.monthly_goals, monthly_spent)
            self.view.load_transactions(self.transactions)
            self.save_data()
        else:
            self.view.show_error("삭제 오류", "선택한 목표가 존재하지 않습니다.")

    def show_monthly_statistics(self):
        stats = defaultdict(int)
        for t in self.transactions:
            if t.type == "지출":
                month = t.date[:7]
                stats[month] += t.amount
        self.view.load_goals(self.monthly_goals, stats)

    def calculate_monthly_spent(self):
        monthly_spent = defaultdict(int)
        for t in self.transactions:
            if t.type == "지출":
                month = t.date[:7]
                monthly_spent[month] += t.amount
        return monthly_spent

    def refresh_graph_data(self):
        service = GraphDataService(self.transactions)
        monthly_data = service.get_monthly_data()
        category_data = service.get_category_data()
        self.view.set_graph_data(monthly_data, category_data)
