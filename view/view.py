import os
import sys
from tkinter import messagebox, ttk, StringVar, Frame, Label, Radiobutton
import tkinter.font as tkfont
import tkinter.font as tkfont
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



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
    

def set_global_font():
    style = ttk.Style()
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=13)  # 기본 폰트 크기 변경
    style.configure('.', font=default_font)
    # Treeview 폰트 설정
    tree_font = tkfont.Font(family='NanumGothic', size=9)
    style.configure("Treeview", font=tree_font, rowheight=25)
    style.configure("Treeview.Heading", font=('NanumGothic', 13, 'bold'))

    # Combobox 폰트 설정
    style.configure("TCombobox", font=('Arial', 10))

class View:
    def __init__(self, root):
        self.root = root
        self.root.title("가계부")
        set_global_font()  # 폰트 크기 변경
        #self.root.geometry("1000x800")
        # 전체화면 설정
        # 모니터 화면 크기 구해서 창 크기 설정
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")  # 화면 전체 크기로 창 설정

        self.balance_var = StringVar(value="잔액: 0원")
        self.transaction_type = StringVar(value="수입")
        self.category_var = StringVar(value="일반")

        self.on_add = None
        self.on_delete = None
        self.on_edit = None
        self.on_set_goal = None
        self.on_show_monthly_stats = None
        self.on_edit_goal = None
        self.on_delete_goal = None

        self.create_widgets()


    def create_widgets(self):
        # 잔액 및 진행률
        self.balance_label = Label(self.root, textvariable=self.balance_var, font=("Arial", 14, "bold"))
        self.balance_label.grid(row=0, column=0, columnspan=3, pady=(10, 15), sticky="w")

        # 날짜 입력
        Label(self.root, text="날짜").grid(row=1, column=0, sticky="w", padx=(10,5))
        self.date_input = DateInput(self.root)
        self.date_input.grid(row=1, column=1, columnspan=2, sticky="w")

        # 금액, 메모, 유형, 카테고리
        Label(self.root, text="금액").grid(row=2, column=0, sticky="w", padx=(10,5), pady=5)
        self.amount_entry = ttk.Entry(self.root)
        self.amount_entry.grid(row=2, column=1, columnspan=2, sticky="ew", pady=5)

        Label(self.root, text="메모").grid(row=3, column=0, sticky="w", padx=(10,5), pady=5)
        self.memo_entry = ttk.Entry(self.root)
        self.memo_entry.grid(row=3, column=1, columnspan=2, sticky="ew", pady=5)

        Label(self.root, text="유형").grid(row=4, column=0, sticky="w", padx=(10,5), pady=5)
        Radiobutton(self.root, text="수입", variable=self.transaction_type, value="수입").grid(row=4, column=1, sticky='w')
        Radiobutton(self.root, text="지출", variable=self.transaction_type, value="지출").grid(row=4, column=2, sticky='w')

        Label(self.root, text="카테고리").grid(row=5, column=0, sticky="w", padx=(10,5), pady=5)
        self.category_combo = ttk.Combobox(self.root, textvariable=self.category_var, values=["교통","저축","주거","용돈","식비","의료","문화","교육","통신","기타"])
        self.category_combo.grid(row=5, column=1, columnspan=2, sticky="ew", pady=5)
        self.category_combo.current(0)

        # 거래 추가 버튼
        self.add_button = ttk.Button(self.root, text="추가", command=self.on_add_click)
        self.add_button.grid(row=6, column=2, sticky="e", pady=(10, 15))

        # 거래 내역 트리뷰
        self.transaction_list = ttk.Treeview(self.root, columns=("날짜", "금액", "유형", "카테고리", "메모","잔액"), show="headings", height=15)
        for col in ("날짜", "금액", "유형", "카테고리", "메모","잔액"):
            self.transaction_list.heading(col, text=col)
            self.transaction_list.column(col, width=110)
        self.transaction_list.grid(row=7, column=0, columnspan=3, padx=10, sticky="nsew")
        # create_widgets 안에 추가
        self.transaction_list.tag_configure("negative", foreground="red")

        # 삭제, 수정 버튼
        self.delete_button = ttk.Button(self.root, text="삭제", command=self.on_delete_click)
        self.delete_button.grid(row=8, column=0, sticky="ew", padx=10, pady=10)

        self.edit_button = ttk.Button(self.root, text="수정", command=self.on_edit_click)
        self.edit_button.grid(row=8, column=1, sticky="ew", padx=10, pady=10)


        # 목표 설정 영역
        Label(self.root, text="목표 설정 (년-월)").grid(row=9, column=0, sticky="w", padx=(10,5))
        self.goal_month_input = MonthInput(self.root)
        self.goal_month_input.grid(row=9, column=1, sticky="w")
        self.goal_amount_entry = ttk.Entry(self.root)
        self.goal_amount_entry.grid(row=9, column=2, sticky="ew")

        # 목표 설정, 수정, 삭제 버튼 한 줄에 배치
        self.set_goal_button = ttk.Button(self.root, text="목표 설정", command=self.on_set_goal_click)
        self.set_goal_button.grid(row=10, column=0, sticky="ew", padx=10, pady=5)
        self.edit_goal_button = ttk.Button(self.root, text="목표 수정", command=self.on_edit_goal_click)
        self.edit_goal_button.grid(row=10, column=1, sticky="ew", padx=10, pady=5)
        self.delete_goal_button = ttk.Button(self.root, text="목표 삭제", command=self.on_delete_goal_click)
        self.delete_goal_button.grid(row=10, column=2, sticky="ew", padx=10, pady=5)

        # 목표 리스트 트리뷰
        self.goal_list = ttk.Treeview(self.root, columns=("월", "목표지출액", "진행률"), show="headings", height=7)
        self.goal_list.heading("월", text="월")
        self.goal_list.heading("목표지출액", text="목표지출액")
        self.goal_list.heading("진행률", text="진행률")
        self.goal_list.column("월", width=100)
        self.goal_list.column("목표지출액", width=120)
        self.goal_list.column("진행률", width=100)
        self.goal_list.grid(row=11, column=0, columnspan=3, padx=10, sticky="nsew")

        # 그래프 프레임 - 오른쪽에 크게 배치 (row 1~11)
        self.graph_frame = Frame(self.root, width=400, height=600, relief="sunken", borderwidth=1)
        self.graph_frame.grid(row=1, column=3, rowspan=11, padx=15, pady=10, sticky="nsew")

        # 그리드 가중치 설정 (리사이징시 동작)
        self.root.grid_rowconfigure(7, weight=1)
        self.root.grid_rowconfigure(11, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)


    # 이벤트 핸들러들
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

    def on_edit_goal_click(self):
        selected = self.goal_list.selection()
        if selected and self.on_edit_goal:
            values = self.goal_list.item(selected[0])["values"]
            year_month = values[0]
            amount = self.goal_amount_entry.get()
            self.on_edit_goal(year_month, amount)

    def on_delete_goal_click(self):
        selected = self.goal_list.selection()
        if selected and self.on_delete_goal:
            values = self.goal_list.item(selected[0])["values"]
            year_month = values[0]
            self.on_delete_goal(year_month)

    def on_show_monthly_stats_click(self):
        if self.on_show_monthly_stats:
            self.on_show_monthly_stats()

    # Controller 연결
    def set_controller(self, controller):
        self.on_add = controller.add_transaction
        self.on_delete = controller.delete_transaction
        self.on_edit = controller.edit_transaction
        self.on_set_goal = controller.set_goal
        self.on_show_monthly_stats = controller.show_monthly_statistics
        self.on_edit_goal = controller.edit_goal
        self.on_delete_goal = controller.delete_goal
        # 자동 그래프 업데이트 연결 (컨트롤러에서 데이터를 받아와서 그래프 세팅)
        if hasattr(controller, "get_all_transactions"):
            monthly_data, category_data = controller.get_all_transactions()
            self.set_graph_data(monthly_data, category_data)

    # 거래내역 관련
    def add_transaction_to_list(self, t , current_balance):
        self.transaction_list.insert('', 'end', values=(t.date, t.amount, t.type, t.category, t.memo, f"{current_balance}원"))
        self.sort_transaction_list()

    def remove_transaction_from_list(self, item_id):
        self.transaction_list.delete(item_id)

    def update_transaction_in_list(self, item_id, date, amount, type_, category, memo):
        self.transaction_list.item(item_id, values=(date, amount, type_, category, memo))
        self.sort_transaction_list()

    def get_transaction_values(self, item_id):
        return self.transaction_list.item(item_id)["values"]

    """def load_transactions(self, transactions):
        for item in self.transaction_list.get_children():
            self.transaction_list.delete(item)
        for t in sorted(transactions, key=lambda x: x.date):
            self.add_transaction_to_list(t)"""
    def load_transactions(self, transactions):
        self.transaction_list.delete(*self.transaction_list.get_children())
        balance = 0
        # 날짜 순 정렬 후
        for t in sorted(transactions, key=lambda x: x.date):
            if t.type == "수입":
                balance += t.amount
            else:
                balance -= t.amount
            # 트리뷰에 추가, 남은 금액 같이 표시
            tag = "negative" if balance < 0 else ""
            self.transaction_list.insert(
                '',
                'end',
                values=(t.date, t.amount, t.type, t.category, t.memo, f"{balance}원")
            )

    def sort_transaction_list(self):
        # 날짜 순 정렬
        items = [(self.transaction_list.item(i)["values"][0], i) for i in self.transaction_list.get_children()]
        items.sort(key=lambda x: x[0])
        for index, (date, item_id) in enumerate(items):
            self.transaction_list.move(item_id, '', index)

    # 목표 관련
    def load_goals(self, goal_dict, monthly_spent):
        # monthly_spent 인자 받도록 수정
        self.goal_list.delete(*self.goal_list.get_children())
        for month, goal_amount in sorted(goal_dict.items()):
            spent = monthly_spent.get(month, 0)
            percent = (spent / goal_amount * 100) if goal_amount else 0
            percent_str = f"{percent:.1f}%" if goal_amount else "0%"
            self.goal_list.insert('', 'end', values=(month, f"{goal_amount}원", percent_str))


    # 상태 업데이트
    def update_balance(self, total_balance):
        self.balance_var.set(f"잔액: {total_balance}원")
        # 음수일 경우 빨간색, 양수일 경우 검은색
        if total_balance < 0:
            self.balance_label.config(fg="red")
        else:
            self.balance_label.config(fg="black")

    def update_progress(self, total_balance, monthly_goals):
        """# 현재 월(YYYY-MM) 기준 목표 가져오기
        current_month = datetime.now().strftime("%Y-%m")
        goal = monthly_goals.get(current_month, 0)
        if goal:
            percent = (total_balance / goal) * 100
            self.progress_var.set(f"목표 대비 진행률: {percent:.1f}%")
        else:
            self.progress_var.set("목표 대비 진행률: 목표 없음")"""
        pass

    # 알림창
    def show_error(self, title, message):
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)
    
      # 그래프 호출 함수
    def set_graph_data(self, monthly_data, category_data):
        self.monthly_data = monthly_data
        self.category_data = category_data
        self.show_graphs(monthly_data, category_data)

    def show_graphs(self, monthly_data, category_data):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # 폰트 경로 지정
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts", "NanumGothic.ttf"))
        font_prop = font_manager.FontProperties(fname=font_path)

        # 꺾은선 그래프 (기존 코드와 동일)
        months = sorted(monthly_data.keys())[-12:]
        income = [monthly_data[m]["수입"] for m in months]
        expense = [monthly_data[m]["지출"] for m in months]

        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.plot(months, income, marker='o', label='수입', color='green')
        ax1.plot(months, expense, marker='o', label='지출', color='red')
        ax1.set_title("월별 수입/지출", fontproperties=font_prop)
        ax1.set_xlabel("월", fontproperties=font_prop)
        ax1.set_ylabel("금액", fontproperties=font_prop)
        ax1.legend(prop=font_prop)
        ax1.grid(True)
        fig1.tight_layout()

        canvas1 = FigureCanvasTkAgg(fig1, master=self.graph_frame)
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # 막대 그래프
        if category_data:
            latest_month = sorted(category_data.keys())[-1]
            category_expense = category_data[latest_month]
            labels = list(category_expense.keys())
            values = list(category_expense.values())

            num_bars = len(labels)
            
            # 막대 개수가 적을 때 기준이 되는 최대 막대 개수
            # 이 값을 조절하여 고정 너비를 유지할 막대 개수 상한을 설정할 수 있습니다.
            MAX_FIXED_WIDTH_BARS = 5 
            # 막대 개수가 적을 때 사용할 고정 너비 (0.0~1.0 사이, 1.0은 막대가 꽉 참)
            FIXED_BAR_WIDTH = 0.5 

            if num_bars <= MAX_FIXED_WIDTH_BARS:
                # 막대 개수가 적을 때는 고정 너비를 사용
                bar_width = FIXED_BAR_WIDTH
                x_min = -0.5 
                x_max = num_bars - 0.5 
            else:
                # 막대 개수가 많아질 때는 공간에 맞춰 너비를 자동으로 줄임
                #  전체 X축 공간 대비 막대가 차지하는 비율
                bar_width = 0.8 / num_bars 
                # X축 범위는 전체 막대가 보이도록 설정
                x_min = -0.5
                x_max = num_bars - 0.5
            # --- 변경된 막대 너비 및 X축 범위 조절 로직 끝 ---


            if values:
                fig2, ax2 = plt.subplots(figsize=(6, 4))
                bars = ax2.bar(labels, values, width=bar_width, align='center', color='skyblue')
                ax2.set_title(f"{latest_month} 카테고리별 지출", fontproperties=font_prop)
                ax2.set_xlabel("카테고리", fontproperties=font_prop)
                ax2.set_ylabel("금액", fontproperties=font_prop)
                
                # X축 눈금 위치를 명시적으로 설정하고 레이블 지정 (폰트 설정 포함)
                x_positions = range(num_bars)
                ax2.set_xticks(x_positions) 
                ax2.set_xticklabels(labels, fontproperties=font_prop) 
                
                # 계산된 x_min, x_max를 사용하여 X축 범위 설정
                ax2.set_xlim(x_min, x_max) 
                
                fig2.tight_layout()

                # 각 막대 위에 금액 표시
                for bar, value in zip(bars, values):
                    # 금액 텍스트 위치를 막대 높이보다 약간 위로 조정하여 겹치지 않도록 함
                    # '5'는 픽셀 단위가 아닌 데이터 단위의 여백이므로, 그래프 크기나 데이터 값에 따라 조절할 수 있습니다.
                    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, f"{value}원", 
                            ha='center', va='bottom', fontproperties=font_prop, fontsize=9)

                canvas2 = FigureCanvasTkAgg(fig2, master=self.graph_frame)
                canvas2.draw()
                canvas2.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # 그래프 프레임 그리드 확장 설정
        self.graph_frame.grid_rowconfigure(0, weight=3)
        self.graph_frame.grid_rowconfigure(1, weight=2)
        self.graph_frame.grid_columnconfigure(0, weight=1)
