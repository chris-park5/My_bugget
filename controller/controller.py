from model.transaction import Transaction
from collections import defaultdict
from datetime import datetime
from tkinter import messagebox
import json
import os

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
        if os.path.exists(TRANSACTION_FILE):
            with open(TRANSACTION_FILE, encoding="utf-8") as f:
                for data in json.load(f):
                    t = Transaction(**data)
                    self.transactions.append(t)
                    self.balance += t.amount if t.type == "수입" else -t.amount

        if os.path.exists(GOAL_FILE):
            with open(GOAL_FILE, encoding="utf-8") as f:
                self.monthly_goals = json.load(f)

        self.view.load_transactions(self.transactions)
        self.view.update_balance(self.balance)
        self.view.update_progress(self.balance)

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

        self.view.add_transaction_to_list(transaction)
        self.view.update_balance(self.balance)
        self.view.update_progress(self.balance)
        self.save_data()

    def delete_transaction(self, item_id):
        values = self.view.get_transaction_values(item_id)
        amount = int(values[1])
        type_ = values[2]

        self.transactions = [t for t in self.transactions if (t.date, t.amount, t.type, t.category, t.memo) != tuple(values)]
        self.balance -= amount if type_ == "수입" else -amount

        self.view.remove_transaction_from_list(item_id)
        self.view.update_balance(self.balance)
        self.view.update_progress(self.balance)
        self.save_data()

    def edit_transaction(self, item_id, date, amount, type_, category, memo):
        try:
            amount = int(amount)
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            self.view.show_error("입력 오류", "날짜는 YYYY-MM-DD 형식, 금액은 숫자여야 합니다.")
            return

        old_values = self.view.get_transaction_values(item_id)
        old_amount = int(old_values[1])
        old_type = old_values[2]

        for t in self.transactions:
            if (t.date, t.amount, t.type, t.category, t.memo) == tuple(old_values):
                t.date, t.amount, t.type, t.category, t.memo = date, amount, type_, category, memo
                break

        self.balance -= old_amount if old_type == "수입" else -old_amount
        self.balance += amount if type_ == "수입" else -amount

        self.view.update_transaction_in_list(item_id, date, amount, type_, category, memo)
        self.view.update_balance(self.balance)
        self.view.update_progress(self.balance)
        self.save_data()

    def set_goal(self, year_month, amount_str):
        try:
            if len(year_month) != 7 or year_month[4] != '-':
                raise ValueError("형식 오류")

            amount = int(amount_str)
            self.monthly_goals[year_month] = amount
            self.view.show_info("목표 설정", f"{year_month} 월 목표: {amount}원 저장 완료")
            self.save_data()
        except Exception:
            self.view.show_error("입력 오류", "목표 형식은 YYYY-MM 형식과 금액으로 입력해주세요.")

    def show_monthly_statistics(self):
        stats = defaultdict(int)
        for t in self.transactions:
            if t.type == "지출":
                month = t.date[:7]  # YYYY-MM
                stats[month] += t.amount

        result_lines = []
        for month, spent in sorted(stats.items()):
            goal = self.monthly_goals.get(month)
            if goal:
                percent = (spent / goal) * 100
                result_lines.append(f"{month} 지출: {spent}원 / 목표: {goal}원 ({percent:.1f}%)")
            else:
                result_lines.append(f"{month} 지출: {spent}원 (목표 없음)")

        self.view.show_statistics_popup(result_lines)