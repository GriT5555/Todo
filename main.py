import tkinter as tk
from tkinter import ttk

from app.ui.task_board import WINDOW_BG, TaskBoard


def main() -> None:
    root = tk.Tk()
    root.title("2Do")
    root.geometry("640x720")
    root.minsize(520, 560)
    root.configure(bg=WINDOW_BG)

    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    board = TaskBoard(root)
    board.grid(row=0, column=0, sticky="nsew")

    root.mainloop()


if __name__ == "__main__":
    main()
