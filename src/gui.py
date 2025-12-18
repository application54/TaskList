# Модуль графического интерфейса

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
from datetime import datetime
from src.database import DatabaseManager
from src.config import APP_NAME

# Класс графического интерфейса менеджера паролей
class TaskManagerGUI:

    # Инициализация главного окна
    def __init__(self, root):
        self.root = root
        self.db = DatabaseManager()
        self.root.title(APP_NAME)
        self.root.geometry("1000x700")
        self.current_filter = "all"
        self.create_widgets()
        self.refresh_tasks()
        self.update_statistics()

    # Создание всех элементов интерфейса
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill='x', pady=(0, 10))
        ttk.Button(filter_frame, text="Все задачи",
                   command=lambda: self.set_filter("all")).pack(side='left', padx=2)
        ttk.Button(filter_frame, text="Активные",
                   command=lambda: self.set_filter("active")).pack(side='left', padx=2)
        ttk.Button(filter_frame, text="Выполненные",
                   command=lambda: self.set_filter("completed")).pack(side='left', padx=2)
        search_frame = ttk.Frame(filter_frame)
        search_frame.pack(side='right', padx=10)
        ttk.Label(search_frame, text="Поиск:").pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side='left', padx=(0, 5))
        self.search_entry.bind('<KeyRelease>', lambda e: self.refresh_tasks())
        ttk.Button(search_frame, text="Очистить",
                   command=self.clear_search).pack(side='left')
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True)
        v_scrollbar = ttk.Scrollbar(tree_frame)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')
        columns = ('Статус', 'Приоритет', 'Название', 'Описание', 'Создана', 'Срок', 'ID')
        self.tree = ttk.Treeview(tree_frame, columns=columns,
                                 show='headings', height=20,
                                 yscrollcommand=v_scrollbar.set,
                                 xscrollcommand=h_scrollbar.set,
                                 selectmode='browse')
        self.tree.heading('Статус', text='✓')
        self.tree.heading('Приоритет', text='★')
        self.tree.heading('Название', text='Название задачи')
        self.tree.heading('Описание', text='Описание')
        self.tree.heading('Создана', text='Создана')
        self.tree.heading('Срок', text='Срок')
        self.tree.heading('ID', text='ID')
        self.tree.column('Статус', width=50, anchor='center')
        self.tree.column('Приоритет', width=50, anchor='center')
        self.tree.column('Название', width=200)
        self.tree.column('Описание', width=300)
        self.tree.column('Создана', width=120)
        self.tree.column('Срок', width=120)
        self.tree.column('ID', width=50)
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        self.tree.bind('<Double-Button-1>', self.edit_task_dialog)
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill='x', pady=(10, 0))
        ttk.Button(action_frame, text="Добавить задачу",
                   command=self.add_task_dialog).pack(side='left', padx=2)
        ttk.Button(action_frame, text="Пометить выполненной",
                   command=self.toggle_task_status).pack(side='left', padx=2)
        ttk.Button(action_frame, text="Редактировать",
                   command=self.edit_task_dialog).pack(side='left', padx=2)
        ttk.Button(action_frame, text="Удалить",
                   command=self.delete_task).pack(side='left', padx=2)
        ttk.Button(action_frame, text="Удалить выполненные",
                   command=self.delete_completed_tasks).pack(side='left', padx=2)
        stats_frame = ttk.LabelFrame(main_frame, text="Статистика", padding="10")
        stats_frame.pack(fill='x', pady=(10, 0))
        self.stats_label = ttk.Label(stats_frame,
                                     text="Всего: 0 | Выполнено: 0 | Активных: 0 | Просрочено: 0")
        self.stats_label.pack()

    # Установка фильтра отображения задач
    def set_filter(self, filter_type):
        self.current_filter = filter_type
        self.refresh_tasks()

    # Очистка поискового запроса
    def clear_search(self):
        self.search_var.set("")
        self.refresh_tasks()

    # Обновление списка задач в дереве
    def refresh_tasks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        tasks = self.db.get_all_tasks(self.current_filter, self.search_var.get())
        for task in tasks:
            status_icon = "✓" if task['status'] == 1 else "○"
            priority_icon = ""
            if task['priority'] == 1:
                priority_icon = "●"
            elif task['priority'] == 2:
                priority_icon = "▲"
            elif task['priority'] == 3:
                priority_icon = "‼"
            created_date = self.format_date(task['created_at'])
            deadline_date = self.format_date(task['deadline']) if task['deadline'] else ""
            if task['deadline'] and task['status'] == 0:
                try:
                    deadline = datetime.fromisoformat(task['deadline'])
                    if deadline < datetime.now():
                        deadline_date = "🚨 " + deadline_date
                except:
                    pass
            tags = ('completed',) if task['status'] == 1 else ()
            item = self.tree.insert('', 'end', values=(
                status_icon,
                priority_icon,
                task['title'],
                task['description'],
                created_date,
                deadline_date,
                task['id']
            ), tags=tags)
        self.tree.tag_configure('completed', foreground='gray')
        self.update_statistics()

    # Форматирование даты для отображения
    def format_date(self, date_string):
        if not date_string:
            return ""
        try:
            date_obj = datetime.fromisoformat(date_string)
            return date_obj.strftime("%d.%m.%Y")
        except:
            return date_string

    # Обновление отображения статистики
    def update_statistics(self):
        stats = self.db.get_statistics()
        text = f"Всего: {stats['total']} | Выполнено: {stats['completed']} | Активных: {stats['active']} | Просрочено: {stats['overdue']}"
        self.stats_label.config(text=text)

    # Открытие диалогового окна для добавления новой задачи
    def add_task_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить задачу")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'500x400+{x}+{y}')
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill='both', expand=True)
        ttk.Label(form_frame, text="Название:*").grid(row=0, column=0, sticky='w', pady=5)
        title_var = tk.StringVar()
        title_entry = ttk.Entry(form_frame, textvariable=title_var, width=40)
        title_entry.grid(row=0, column=1, pady=5, padx=10, sticky='w')
        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, sticky='nw', pady=5)
        desc_text = tk.Text(form_frame, width=40, height=8)
        desc_text.grid(row=1, column=1, pady=5, padx=10, sticky='w')
        ttk.Label(form_frame, text="Приоритет:").grid(row=2, column=0, sticky='w', pady=5)
        priority_var = tk.IntVar(value=1)
        priority_frame = ttk.Frame(form_frame)
        priority_frame.grid(row=2, column=1, pady=5, padx=10, sticky='w')
        ttk.Radiobutton(priority_frame, text="Низкий", variable=priority_var, value=1).pack(side='left', padx=5)
        ttk.Radiobutton(priority_frame, text="Средний", variable=priority_var, value=2).pack(side='left', padx=5)
        ttk.Radiobutton(priority_frame, text="Высокий", variable=priority_var, value=3).pack(side='left', padx=5)
        ttk.Label(form_frame, text="Срок (ГГГГ-ММ-ДД):").grid(row=3, column=0, sticky='w', pady=5)
        deadline_var = tk.StringVar()
        deadline_entry = ttk.Entry(form_frame, textvariable=deadline_var, width=20)
        deadline_entry.grid(row=3, column=1, pady=5, padx=10, sticky='w')
        ttk.Label(form_frame, text="Например: 2024-12-31", font=('Arial', 9)).grid(row=4, column=1, sticky='w', padx=10)
        def save_task():
            title = title_var.get().strip()
            if not title:
                messagebox.showwarning("Ошибка", "Введите название задачи!")
                return
            description = desc_text.get('1.0', 'end-1c').strip()
            priority = priority_var.get()
            deadline = deadline_var.get().strip() or None
            if deadline:
                try:
                    datetime.fromisoformat(deadline)
                except ValueError:
                    messagebox.showwarning("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
                    return
            if self.db.add_task(title, description, priority, deadline):
                messagebox.showinfo("Успех", "Задача добавлена!")
                dialog.destroy()
                self.refresh_tasks()
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить задачу")
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Сохранить", command=save_task).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side='left', padx=5)
        title_entry.focus()

    # Открытие диалогового окна для редактирования выбранной задачи
    def edit_task_dialog(self, event=None):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите задачу для редактирования")
            return
        item = self.tree.item(selection[0])
        task_id = item['values'][6]
        tasks = self.db.get_all_tasks("all", "")
        task_data = None
        for task in tasks:
            if task['id'] == task_id:
                task_data = task
                break
        if not task_data:
            messagebox.showerror("Ошибка", "Задача не найдена")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать задачу")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'500x400+{x}+{y}')
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill='both', expand=True)
        ttk.Label(form_frame, text="Название:*").grid(row=0, column=0, sticky='w', pady=5)
        title_var = tk.StringVar(value=task_data['title'])
        title_entry = ttk.Entry(form_frame, textvariable=title_var, width=40)
        title_entry.grid(row=0, column=1, pady=5, padx=10, sticky='w')
        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, sticky='nw', pady=5)
        desc_text = tk.Text(form_frame, width=40, height=8)
        desc_text.insert('1.0', task_data['description'])
        desc_text.grid(row=1, column=1, pady=5, padx=10, sticky='w')
        ttk.Label(form_frame, text="Приоритет:").grid(row=2, column=0, sticky='w', pady=5)
        priority_var = tk.IntVar(value=task_data['priority'])
        priority_frame = ttk.Frame(form_frame)
        priority_frame.grid(row=2, column=1, pady=5, padx=10, sticky='w')
        ttk.Radiobutton(priority_frame, text="Низкий", variable=priority_var, value=1).pack(side='left', padx=5)
        ttk.Radiobutton(priority_frame, text="Средний", variable=priority_var, value=2).pack(side='left', padx=5)
        ttk.Radiobutton(priority_frame, text="Высокий", variable=priority_var, value=3).pack(side='left', padx=5)
        ttk.Label(form_frame, text="Статус:").grid(row=3, column=0, sticky='w', pady=5)
        status_var = tk.IntVar(value=task_data['status'])
        ttk.Checkbutton(form_frame, text="Выполнена", variable=status_var).grid(row=3, column=1, sticky='w', padx=10)
        ttk.Label(form_frame, text="Срок (ГГГГ-ММ-ДД):").grid(row=4, column=0, sticky='w', pady=5)
        deadline_var = tk.StringVar(value=task_data['deadline'] or "")
        deadline_entry = ttk.Entry(form_frame, textvariable=deadline_var, width=20)
        deadline_entry.grid(row=4, column=1, pady=5, padx=10, sticky='w')

        # Сохранение выбранной задачи
        def save_changes():
            title = title_var.get().strip()
            if not title:
                messagebox.showwarning("Ошибка", "Введите название задачи!")
                return
            description = desc_text.get('1.0', 'end-1c').strip()
            priority = priority_var.get()
            status = status_var.get()
            deadline = deadline_var.get().strip() or None
            if deadline:
                try:
                    datetime.fromisoformat(deadline)
                except ValueError:
                    messagebox.showwarning("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
                    return
            if self.db.update_task(task_id, title, description, priority, deadline):
                if status != task_data['status']:
                    self.db.update_task_status(task_id, status)
                messagebox.showinfo("Успех", "Задача обновлена!")
                dialog.destroy()
                self.refresh_tasks()
            else:
                messagebox.showerror("Ошибка", "Не удалось обновить задачу")
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Сохранить", command=save_changes).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить",
                   command=lambda: self.delete_task_confirm(task_id, dialog)).pack(side='left', padx=5)
        title_entry.focus()

    # Изменение статуса задачи
    def toggle_task_status(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите задачу")
            return
        item = self.tree.item(selection[0])
        task_id = item['values'][6]
        current_status_icon = item['values'][0]
        new_status = 0 if current_status_icon == "✓" else 1
        if self.db.update_task_status(task_id, new_status):
            self.refresh_tasks()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить статус задачи")

    # Удаление выбранной задачи
    def delete_task(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите задачу для удаления")
            return
        item = self.tree.item(selection[0])
        task_id = item['values'][6]
        if messagebox.askyesno("Подтверждение", "Удалить выбранную задачу?"):
            if self.db.delete_task(task_id):
                messagebox.showinfo("Успех", "Задача удалена")
                self.refresh_tasks()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить задачу")

    # Подтверждение удаления задачи из диалогового окна редактирования
    def delete_task_confirm(self, task_id, parent_window=None):
        if messagebox.askyesno("Подтверждение", "Удалить эту задачу?"):
            if self.db.delete_task(task_id):
                if parent_window:
                    parent_window.destroy()
                messagebox.showinfo("Успех", "Задача удалена")
                self.refresh_tasks()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить задачу")

    # Удаление всех выполненных задач
    def delete_completed_tasks(self):
        if messagebox.askyesno("Подтверждение", "Удалить все выполненные задачи?"):
            if self.db.delete_completed_tasks():
                messagebox.showinfo("Успех", "Выполненные задачи удалены")
                self.refresh_tasks()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить выполненные задачи")