import tkinter as tk
from gui import DealForgeApp


def main():
    root = tk.Tk()
    app = DealForgeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()