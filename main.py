import tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

from controller.controller import LedgerController
from view.view import View

if __name__ == "__main__":
    # 폰트 경로 지정
    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fonts", "NanumGothic.ttf"))

    # 폰트 캐시에 폰트 등록
    fm.fontManager.addfont(font_path)

    # 폰트 이름 가져오기
    font_prop = fm.FontProperties(fname=font_path)
    font_name = font_prop.get_name()
    print("폰트 경로:", font_path)
    print("폰트 이름:", font_name)

    # matplotlib 기본 폰트 설정
    plt.rcParams['font.family'] = font_name
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

    # tkinter GUI 시작
    root = tk.Tk()
    view = View(root)
    controller = LedgerController(view)
    root.mainloop()