import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import sys  # sys 추가

from controller.controller import LedgerController
from view.view import View

if __name__ == "__main__":
    # 폰트 경로 지정
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fonts", "NanumGothic.ttf"))
    fm.fontManager.addfont(font_path)
    font_prop = fm.FontProperties(fname=font_path)
    font_name = font_prop.get_name()
    plt.rcParams['font.family'] = font_name
    plt.rcParams['axes.unicode_minus'] = False

    # tkinter GUI 시작
    root = tk.Tk()

    # 창 닫기 시 완전 종료 처리
    def on_close():
        root.destroy()
        sys.exit()

    root.protocol("WM_DELETE_WINDOW", on_close)

    view = View(root)
    controller = LedgerController(view)
    root.mainloop()
