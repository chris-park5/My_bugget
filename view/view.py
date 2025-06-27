from tkinter import messagebox, ttk, StringVar, Frame, Label, Button, Radiobutton
from datetime import datetime

class DateInput(Frame):
    def __init__(self, master):
        super().__init__(master)
        now = datetime.now()
        self.year_var = StringVar(value=str(now.year))
        self.month_var = StringVar(value=str(now.month).zfill(2))
        self.day_var = StringVar(value=str(now.day).zfill(2))

        self.year_box = ttk.Combobox(self, textvariable=self.year_var, width=5, values=[str(y) for y in range(2000, 2101)])
        self.month_box = ttk.Combobox(self, textvariable=self.month_var, width=3, values=[str(m).zfill(2) for m in range(1, 13)])
        self.day_box = ttk.Combobox(self, textvariable=self.day_var, width=3, values=[str(d).zfill(2) for d in range(1, 32)])

        self.year_box.pack(side="left")
        Label(self, text="-").pack(side="left")
        self.month_box.pack(side="left")
        Label(self, text="-").pack(side="left")
        self.day_box.pack(side="left")

    def get_date(self):
        return f"{self.year_var.get()}-{self.month_var.get()}-{self.day_var.get()}"

class MonthInput(Frame):
    def __init__(self, master):
        super().__init__(master)
        now = datetime.now()
        self.year_var = StringVar(value=str(now.year))
        self.month_var = StringVar(value=str(now.month).zfill(2))

        self.year_box = ttk.Combobox(self, textvariable=self.year_var, width=5, values=[str(y) for y in range(2000, 2101)])
        self.month_box = ttk.Combobox(self, textvariable=self.month_var, width=3, values=[str(m).zfill(2) for m in range(1, 13)])

        self.year_box.pack(side="left")
        Label(self, text="-").pack(side="left")
        self.month_box.pack(side="left")

    def get_month(self):
        return f"{self.year_var.get()}-{self.month_var.get()}"

class View:
    def __init__(self, root):
        self.root = root
        self.root.title("가계부")
        self.root.geometry("650x500")

        # 상태 변수
        self.balance_var = StringVar(value="남은 금액: 0원")
        self.progress_var = StringVar(value="목표 대비 진행률: 0%")
        self.transaction_type = StringVar(value="수입")
        self.category_var = StringVar(value="일반")

        # 컨트롤러 연결용
        self.on_add = None
        self.on_delete = None
        self.on_edit = None
        self.on_set_goal = None
        self.on_show_monthly_stats = None

        self.create_widgets()

    def create_widgets(self):
        # 잔액, 진행률 표시
        Label(self.root, textvariable=self.balance_var, font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, pady=10)
        Label(self.root, textvariable=self.progress_var, font=("Arial", 11)).grid(row=1, column=0, columnspan=3, pady=5)

        # 날짜 입력 (년-월-일 콤보박스)
        Label(self.root, text="날짜").grid(row=2, column=0)
        self.date_input = DateInput(self.root)
        self.date_input.grid(row=2, column=1, columnspan=2)

        # 금액 입력
        Label(self.root, text="금액").grid(row=3, column=0)
        self.amount_entry = ttk.Entry(self.root)
        self.amount_entry.grid(row=3, column=1, columnspan=2)

        # 메모 입력
        Label(self.root, text="메모").grid(row=4, column=0)
        self.memo_entry = ttk.Entry(self.root)
        self.memo_entry.grid(row=4, column=1, columnspan=2)

        # 유형 라디오 버튼
        Label(self.root, text="유형").grid(row=5, column=0)
        Radiobutton(self.root, text="수입", variable=self.transaction_type, value="수입").grid(row=5, column=1, sticky='w')
        Radiobutton(self.root, text="지출", variable=self.transaction_type, value="지출").grid(row=5, column=2, sticky='w')

        # 카테고리 콤보박스
        Label(self.root, text="카테고리").grid(row=6, column=0)
        self.category_combo = ttk.Combobox(self.root, textvariable=self.category_var, values=["일반", "식비", "교통", "의료", "기타"])
        self.category_combo.grid(row=6, column=1, columnspan=2)
        self.category_combo.current(0)

        # 추가 버튼
        self.add_button = ttk.Button(self.root, text="추가", command=self.on_add_click)
        self.add_button.grid(row=7, column=2, pady=5)

        # 거래내역 리스트
        self.transaction_list = ttk.Treeview(self.root, columns=("날짜", "금액", "유형", "카테고리", "메모"), show="headings")
        for col in ("날짜", "금액", "유형", "카테고리", "메모"):
            self.transaction_list.heading(col, text=col)
            self.transaction_list.column(col, width=100)
        self.transaction_list.grid(row=8, column=0, columnspan=3, pady=10)

        # 삭제 버튼
        self.delete_button = ttk.Button(self.root, text="삭제", command=self.on_delete_click)
        self.delete_button.grid(row=9, column=0, pady=5)

        # 수정 버튼
        self.edit_button = ttk.Button(self.root, text="수정", command=self.on_edit_click)
        self.edit_button.grid(row=9, column=1, pady=5)

        # 목표 설정 (년-월 콤보박스 + 금액 입력)
        Label(self.root, text="목표 설정 (년-월)").grid(row=10, column=0)
        self.goal_month_input = MonthInput(self.root)
        self.goal_month_input.grid(row=10, column=1)
        self.goal_amount_entry = ttk.Entry(self.root)
        self.goal_amount_entry.grid(row=10, column=2)

        # 목표 설정 버튼
        self.set_goal_button = ttk.Button(self.root, text="목표 설정", command=self.on_set_goal_click)
        self.set_goal_button.grid(row=11, column=2, pady=5)

        # 월별 통계 버튼
        self.show_stats_button = ttk.Button(self.root, text="월별 통계 보기", command=self.on_show_monthly_stats_click)
        self.show_stats_button.grid(row=12, column=2, pady=5)

    # 버튼 콜백들
    def on_add_click(self):
        if self.on_add:
            self.on_add(
                self.date_input.get_date(),
                self.amount_entry.get(),
                self.transaction_type.get(),
                self.category_var.get(),
                self.memo_entry.get()
            )

    def on_delete_click(self):
        selected = self.transaction_list.selection()
        if selected and self.on_delete:
            self.on_delete(selected[0])

    def on_edit_click(self):
        selected = self.transaction_list.selection()
        if selected and self.on_edit:
            self.on_edit(
                selected[0],
                self.date_input.get_date(),
                self.amount_entry.get(),
                self.transaction_type.get(),
                self.category_var.get(),
                self.memo_entry.get()
            )

    def on_set_goal_click(self):
        if self.on_set_goal:
            year_month = self.goal_month_input.get_month()
            amount = self.goal_amount_entry.get()
            self.on_set_goal(year_month, amount)

    def on_show_monthly_stats_click(self):
        if self.on_show_monthly_stats:
            self.on_show_monthly_stats()

    # View가 Controller에 연결될 때 호출
    def set_controller(self, controller):
        self.on_add = controller.add_transaction
        self.on_delete = controller.delete_transaction
        self.on_edit = controller.edit_transaction
        self.on_set_goal = controller.set_goal
        self.on_show_monthly_stats = controller.show_monthly_statistics

    # 거래내역 리스트 조작 메서드들
    def add_transaction_to_list(self, t):
        self.transaction_list.insert('', 'end', values=(t.date, t.amount, t.type, t.category, t.memo))

    def remove_transaction_from_list(self, item_id):
        self.transaction_list.delete(item_id)

    def update_transaction_in_list(self, item_id, date, amount, type_, category, memo):
        self.transaction_list.item(item_id, values=(date, amount, type_, category, memo))

    def get_transaction_values(self, item_id):
        return self.transaction_list.item(item_id)["values"]

    def load_transactions(self, transactions):
        for t in transactions:
            self.add_transaction_to_list(t)

    # 상태 표시 업데이트
    def update_balance(self, total_balance):
        self.balance_var.set(f"남은 금액: {total_balance}원")

    def update_progress(self, total_balance):
        # 목표 대비 진행률 표시 (가장 최근 목표 기준)
        current_month = datetime.now().strftime("%Y-%m")
        goal = getattr(self, 'monthly_goals', {}).get(current_month, 0)
        if goal:
            percent = (total_balance / goal) * 100
            self.progress_var.set(f"목표 대비 진행률: {percent:.1f}%")
        else:
            self.progress_var.set("목표 대비 진행률: 목표 없음")

    # 알림창
    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def show_statistics_popup(self, lines):
        messagebox.showinfo("월별 통계", "\n".join(lines))