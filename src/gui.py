# Модуль графического интерфейса

import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
from src.database import DatabaseManager
from src.generator import PasswordGenerator
from src.config import APP_NAME

# Класс графического интерфейса менеджера паролей
class PasswordManagerGUI:

    # Инициализация главного окна
    def __init__(self, root, master_password):
        self.root = root
        self.master_password = master_password
        self.db = DatabaseManager()
        self.generator = PasswordGenerator()
        self.root.title(APP_NAME)
        self.root.geometry("900x650")
        self.password_visible = False
        self.create_widgets()
        self.refresh_passwords()

    # Создание всех виджетов интерфейса
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        self.tab_passwords = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_passwords, text='Мои пароли')
        self.create_passwords_tab()
        self.tab_add = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_add, text='Добавить пароль')
        self.create_add_tab()
        self.tab_generator = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_generator, text='Генератор')
        self.create_generator_tab()

    # Создание вкладки для просмотра паролей
    def create_passwords_tab(self):
        control_frame = ttk.Frame(self.tab_passwords)
        control_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(control_frame, text='Обновить',
                   command=self.refresh_passwords).pack(side='left', padx=5)
        ttk.Label(control_frame, text='Поиск:').pack(side='left', padx=(10, 5))
        self.entry_search = ttk.Entry(control_frame, width=30)
        self.entry_search.pack(side='left', padx=5)
        self.entry_search.bind('<KeyRelease>', lambda e: self.search_passwords())
        columns = ('ID', 'Название', 'Логин', 'Пароль', 'Примечания')
        tree_frame = ttk.Frame(self.tab_passwords)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        v_scrollbar = ttk.Scrollbar(tree_frame)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')
        self.tree = ttk.Treeview(tree_frame, columns=columns,
                                 show='headings', height=20,
                                 yscrollcommand=v_scrollbar.set,
                                 xscrollcommand=h_scrollbar.set,
                                 selectmode='extended')
        column_widths = {'ID': 50, 'Название': 150, 'Логин': 150, 'Пароль': 150, 'Примечания': 200}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), minwidth=50)
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        action_frame = ttk.Frame(self.tab_passwords)
        action_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(action_frame, text='Копировать логин',
                   command=self.copy_username).pack(side='left', padx=5)
        ttk.Button(action_frame, text='Копировать пароль',
                   command=self.copy_password).pack(side='left', padx=5)
        ttk.Button(action_frame, text='Показать/Скрыть пароли',
                   command=self.toggle_visibility).pack(side='left', padx=5)
        ttk.Button(action_frame, text='Удалить',
                   command=self.delete_selected).pack(side='left', padx=5)

    # Создание вкладки для добавления нового пароля
    def create_add_tab(self):
        form_frame = ttk.Frame(self.tab_add)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        ttk.Label(form_frame, text='Название:*').grid(row=0, column=0, sticky='w', pady=10)
        self.entry_title = tk.Entry(form_frame, width=40)
        self.entry_title.grid(row=0, column=1, pady=10, padx=10, sticky='w')
        ttk.Label(form_frame, text='Логин:').grid(row=1, column=0, sticky='w', pady=10)
        self.entry_username = tk.Entry(form_frame, width=40)
        self.entry_username.grid(row=1, column=1, pady=10, padx=10, sticky='w')
        ttk.Label(form_frame, text='Пароль:*').grid(row=2, column=0, sticky='w', pady=10)
        password_frame = ttk.Frame(form_frame)
        password_frame.grid(row=2, column=1, pady=10, padx=10, sticky='w')
        self.entry_password = tk.Entry(password_frame, width=40)
        self.entry_password.pack(side='left')
        ttk.Label(form_frame, text='Примечания:').grid(row=3, column=0, sticky='nw', pady=10)
        self.text_notes = tk.Text(form_frame, width=40, height=5)
        self.text_notes.grid(row=3, column=1, pady=10, padx=10, sticky='w')
        button_frame = ttk.Frame(self.tab_add)
        button_frame.pack(fill='x', padx=20, pady=10)
        ttk.Button(button_frame, text='Сохранить',
                   command=self.save_password).pack(side='left', padx=5)
        ttk.Button(button_frame, text='Очистить',
                   command=self.clear_form).pack(side='left', padx=5)

    # Создание вкладки генератора паролей
    def create_generator_tab(self):
        gen_frame = ttk.Frame(self.tab_generator)
        gen_frame.pack(fill='both', expand=True, padx=20, pady=20)
        ttk.Label(gen_frame, text='Длина:').grid(row=0, column=0, sticky='w', pady=10)
        self.var_length = tk.IntVar(value=16)
        length_frame = ttk.Frame(gen_frame)
        length_frame.grid(row=0, column=1, pady=10, padx=10, sticky='w')
        self.length_scale = ttk.Scale(length_frame, from_=8, to=32, variable=self.var_length,
                                     orient='horizontal', length=200)
        self.length_scale.pack(side='left')
        self.label_length = ttk.Label(length_frame, text='16')
        self.label_length.pack(side='left', padx=10)
        ttk.Label(gen_frame, text='Символы:').grid(row=1, column=0, sticky='w', pady=10)
        self.var_lower = tk.BooleanVar(value=True)
        self.var_upper = tk.BooleanVar(value=True)
        self.var_digits = tk.BooleanVar(value=True)
        self.var_special = tk.BooleanVar(value=False)
        ttk.Checkbutton(gen_frame, text='Строчные (abc)', variable=self.var_lower,
                       command=self.update_generated_password).grid(row=1, column=1, sticky='w')
        ttk.Checkbutton(gen_frame, text='Прописные (ABC)', variable=self.var_upper,
                       command=self.update_generated_password).grid(row=2, column=1, sticky='w')
        ttk.Checkbutton(gen_frame, text='Цифры (123)', variable=self.var_digits,
                       command=self.update_generated_password).grid(row=3, column=1, sticky='w')
        ttk.Checkbutton(gen_frame, text='Спецсимволы (!@#)', variable=self.var_special,
                       command=self.update_generated_password).grid(row=4, column=1, sticky='w')
        ttk.Label(gen_frame, text='Пароль:').grid(row=5, column=0, sticky='w', pady=15)
        self.var_gen_password = tk.StringVar()
        self.entry_gen_password = tk.Entry(gen_frame, textvariable=self.var_gen_password, width=40)
        self.entry_gen_password.grid(row=5, column=1, pady=15, padx=10)
        button_frame = ttk.Frame(self.tab_generator)
        button_frame.pack(fill='x', padx=20, pady=10)
        ttk.Button(button_frame, text='Сгенерировать',
                   command=self.generate_password).pack(side='left', padx=5)
        ttk.Button(button_frame, text='Копировать',
                   command=self.copy_generated).pack(side='left', padx=5)
        self.var_length.trace_add('write', lambda *args: self.update_generated_password())
        self.generate_password()

    # Обновление сгенерированного пароля
    def update_generated_password(self):
        self.label_length.config(text=str(self.var_length.get()))
        self.generate_password()

    # Обновление списка паролей
    def refresh_passwords(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        passwords = self.db.get_all_passwords(self.master_password)
        for pwd in passwords:
            password_display = pwd['password'] if self.password_visible else '•' * 10
            self.tree.insert('', 'end', values=(
                pwd['id'],
                pwd['title'],
                pwd['username'] or '',
                password_display,
                pwd['notes'] or ''
            ))

    # Поиск паролей по ключевому слову
    def search_passwords(self):
        search_term = self.entry_search.get().lower()
        passwords = self.db.get_all_passwords(self.master_password)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for pwd in passwords:
            if (search_term in pwd['title'].lower() or
                search_term in (pwd['username'] or '').lower() or
                search_term in (pwd['notes'] or '').lower()):
                password_display = pwd['password'] if self.password_visible else '•' * 10
                self.tree.insert('', 'end', values=(
                    pwd['id'],
                    pwd['title'],
                    pwd['username'] or '',
                    password_display,
                    pwd['notes'] or ''
                ))

    # Копирование пароля в буфер обмена
    def copy_password(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите пароль для копирования")
            return
        item = self.tree.item(selection[0])
        password_id = item['values'][0]
        passwords = self.db.get_all_passwords(self.master_password)
        for pwd in passwords:
            if pwd['id'] == password_id:
                pyperclip.copy(pwd['password'])
                messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
                return
        messagebox.showerror("Ошибка", "Не удалось найти пароль")

    # Копирование логина в буфер обмена
    def copy_username(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите запись для копирования логина")
            return
        item = self.tree.item(selection[0])
        password_id = item['values'][0]
        passwords = self.db.get_all_passwords(self.master_password)
        for pwd in passwords:
            if pwd['id'] == password_id:
                username = pwd['username'] or ''
                if username:
                    pyperclip.copy(username)
                    messagebox.showinfo("Успех", "Логин скопирован в буфер обмена")
                else:
                    messagebox.showwarning("Ошибка", "У выбранной записи нет логина")
                return
        messagebox.showerror("Ошибка", "Не удалось найти запись")

    # Переключение видимости паролей
    def toggle_visibility(self):
        self.password_visible = not self.password_visible
        self.refresh_passwords()

    # Удаление выбранной записи
    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Ошибка", "Выберите запись для удаления")
            return
        item = self.tree.item(selection[0])
        password_id = item['values'][0]
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            if self.db.delete_password(password_id):
                messagebox.showinfo("Успех", "Запись удалена")
                self.refresh_passwords()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить запись")

    # Сохранение нового пароля
    def save_password(self):
        title = self.entry_title.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        notes = self.text_notes.get('1.0', 'end-1c').strip()
        if not title:
            messagebox.showwarning("Ошибка", "Введите название!")
            self.entry_title.focus()
            return
        if not password:
            messagebox.showwarning("Ошибка", "Введите пароль!")
            self.entry_password.focus()
            return
        if self.db.add_password(title, "", username, password, notes, self.master_password):
            messagebox.showinfo("Успех", "Пароль сохранен")
            self.clear_form()
            self.refresh_passwords()
            self.notebook.select(0)  # Переходим на вкладку с паролями
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить пароль")

    # Очистка формы добавления пароля
    def clear_form(self):
        self.entry_title.delete(0, 'end')
        self.entry_username.delete(0, 'end')
        self.entry_password.delete(0, 'end')
        self.text_notes.delete('1.0', 'end')
        self.entry_title.focus()

    # Генерация пароля
    def generate_password(self):
        if not (self.var_lower.get() or self.var_upper.get() or
                self.var_digits.get() or self.var_special.get()):
            messagebox.showwarning("Ошибка", "Выберите хотя бы один тип символов!")
            return
        password = self.generator.generate(
            length=self.var_length.get(),
            use_lowercase=self.var_lower.get(),
            use_uppercase=self.var_upper.get(),
            use_digits=self.var_digits.get(),
            use_special=self.var_special.get()
        )
        self.var_gen_password.set(password)

    # Копирование сгенерированного пароля
    def copy_generated(self):
        password = self.var_gen_password.get()
        if password:
            pyperclip.copy(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
        else:
            messagebox.showwarning("Ошибка", "Сначала сгенерируйте пароль")