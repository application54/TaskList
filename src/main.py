# Главный модуль приложения

import tkinter as tk
from tkinter import messagebox
import sys
from src.gui import TaskManagerGUI
from src.config import APP_NAME

# Главная функция приложения
def main():
    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("1000x700")
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'1000x700+{x}+{y}')
    try:
        app = TaskManagerGUI(root)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить приложение:\n{str(e)}")
        sys.exit(1)
    root.mainloop()

# Точка входа в приложение
if __name__ == "__main__":
    main()