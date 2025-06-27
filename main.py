import tkinter as tk
from controller.controller import LedgerController
from view.view import View

if __name__ == "__main__":
    root = tk.Tk()
    view = View(root)
    controller = LedgerController(view)
    root.mainloop()