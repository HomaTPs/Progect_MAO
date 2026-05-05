import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from tkinter import filedialog

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Данные тренировок
        self.trainings = []
        self.filtered_trainings = []
        
        # Файл для сохранения данных
        self.data_file = "trainings.json"
        
        # Загрузка данных из JSON
        self.load_from_json()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
    
    def create_widgets(self):
        # Основной фрейм для ввода данных
        input_frame = tk.LabelFrame(self.root, text="Добавление тренировки", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")
        
        # Поле Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = tk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Поле Тип тренировки
        tk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.type_entry = ttk.Combobox(input_frame, values=["Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Растяжка"], width=17)
        self.type_entry.grid(row=0, column=3, padx=5, pady=5)
        self.type_entry.set("Бег")
        
        # Поле Длительность
        tk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.duration_entry = tk.Entry(input_frame, width=15)
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка Добавить
        add_button = tk.Button(input_frame, text="Добавить тренировку", command=self.add_training, 
                               bg="green", fg="white", font=("Arial", 10, "bold"))
        add_button.grid(row=0, column=6, padx=10, pady=5)
        
        # Фрейм для фильтрации
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(pady=10, padx=10, fill="x")
        
        # Фильтр по типу
        tk.Label(filter_frame, text="Тип тренировки:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_type = ttk.Combobox(filter_frame, values=["Все", "Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Растяжка"], width=17)
        self.filter_type.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type.set("Все")
        self.filter_type.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
        # Фильтр по дате
        tk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.filter_date = tk.Entry(filter_frame, width=20)
        self.filter_date.grid(row=0, column=3, padx=5, pady=5)
        self.filter_date.insert(0, "")
        
        # Кнопки фильтрации
        filter_button = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filters, 
                                  bg="blue", fg="white")
        filter_button.grid(row=0, column=4, padx=5, pady=5)
        
        reset_button = tk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters, 
                                 bg="orange", fg="white")
        reset_button.grid(row=0, column=5, padx=5, pady=5)
        
        # Таблица для отображения тренировок
        table_frame = tk.Frame(self.root)
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Создание таблицы
        columns = ("Дата", "Тип тренировки", "Длительность (мин)")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Тип тренировки", text="Тип тренировки")
        self.tree.heading("Длительность (мин)", text="Длительность (мин)")
        
        # Настройка ширины столбцов
        self.tree.column("Дата", width=150)
        self.tree.column("Тип тренировки", width=200)
        self.tree.column("Длительность (мин)", width=150)
        
        # Добавление полосы прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        delete_button = tk.Button(button_frame, text="Удалить выбранную", command=self.delete_selected, 
                                  bg="red", fg="white")
        delete_button.pack(side="left", padx=5)
        
        save_button = tk.Button(button_frame, text="Сохранить в JSON", command=self.save_to_json, 
                                bg="green", fg="white")
        save_button.pack(side="left", padx=5)
        
        load_button = tk.Button(button_frame, text="Загрузить из JSON", command=self.load_from_json_dialog, 
                                bg="blue", fg="white")
        load_button.pack(side="left", padx=5)
        
        clear_button = tk.Button(button_frame, text="Очистить всё", command=self.clear_all, 
                                 bg="orange", fg="white")
        clear_button.pack(side="left", padx=5)
    
    def validate_date(self, date_string):
        """Проверка корректности формата даты"""
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_duration(self, duration_string):
        """Проверка корректности длительности"""
        try:
            duration = float(duration_string)
            return duration > 0
        except ValueError:
            return False
    
    def add_training(self):
        """Добавление новой тренировки"""
        date = self.date_entry.get().strip()
        training_type = self.type_entry.get().strip()
        duration = self.duration_entry.get().strip()
        
        # Валидация данных
        if not date:
            messagebox.showerror("Ошибка", "Поле 'Дата' не может быть пустым")
            return
        
        if not training_type:
            messagebox.showerror("Ошибка", "Поле 'Тип тренировки' не может быть пустым")
            return
        
        if not duration:
            messagebox.showerror("Ошибка", "Поле 'Длительность' не может быть пустым")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД\nПример: 2024-12-25")
            return
        
        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом!")
            return
        
        # Добавление тренировки
        training = {
            "date": date,
            "type": training_type,
            "duration": float(duration)
        }
        
        self.trainings.append(training)
        self.save_to_json_auto()  # Автоматическое сохранение
        self.apply_filters()  # Обновление отображения
        
        # Очистка полей
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.duration_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Тренировка успешно добавлена!")
    
    def apply_filters(self):
        """Применение фильтров"""
        filter_type = self.filter_type.get()
        filter_date = self.filter_date.get().strip()
        
        self.filtered_trainings = self.trainings.copy()
        
        # Фильтрация по типу
        if filter_type != "Все" and filter_type:
            self.filtered_trainings = [t for t in self.filtered_trainings if t["type"] == filter_type]
        
        # Фильтрация по дате
        if filter_date:
            if self.validate_date(filter_date):
                self.filtered_trainings = [t for t in self.filtered_trainings if t["date"] == filter_date]
            else:
                messagebox.showwarning("Предупреждение", "Неверный формат даты фильтра!")
        
        self.refresh_table()
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_type.set("Все")
        self.filter_date.delete(0, tk.END)
        self.apply_filters()
    
    def refresh_table(self):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполнение таблицы
        for training in self.filtered_trainings:
            self.tree.insert("", tk.END, values=(
                training["date"],
                training["type"],
                f"{training['duration']:.1f}"
            ))
    
    def delete_selected(self):
        """Удаление выбранной тренировки"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту тренировку?"):
            # Получение индекса выбранной записи
            selected_index = self.tree.index(selected_item[0])
            
            # Удаление из фильтрованного списка
            if self.filtered_trainings:
                training_to_delete = self.filtered_trainings[selected_index]
                
                # Удаление из основного списка
                if training_to_delete in self.trainings:
                    self.trainings.remove(training_to_delete)
                
                # Сохранение и обновление
                self.save_to_json_auto()
                self.apply_filters()
                messagebox.showinfo("Успех", "Тренировка удалена")
    
    def save_to_json(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в файл {self.data_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
    
    def save_to_json_auto(self):
        """Автоматическое сохранение в JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка автоматического сохранения: {e}")
    
    def load_from_json(self):
        """Загрузка данных из JSON файла при запуске"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.trainings = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки данных: {e}")
                self.trainings = []
        else:
            # Добавление демо-данных, если файл не существует
            self.trainings = [
                {"date": "2024-12-20", "type": "Бег", "duration": 30.0},
                {"date": "2024-12-21", "type": "Плавание", "duration": 45.0},
                {"date": "2024-12-22", "type": "Силовая", "duration": 60.0}
            ]
            self.save_to_json_auto()
    
    def load_from_json_dialog(self):
        """Загрузка данных из выбранного JSON файла"""
        filename = filedialog.askopenfilename(
            title="Выберите JSON файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.trainings = json.load(f)
                self.apply_filters()
                messagebox.showinfo("Успех", f"Данные загружены из {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
    
    def clear_all(self):
        """Очистка всех данных"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить все тренировки?"):
            self.trainings = []
            self.save_to_json_auto()
            self.apply_filters()
            messagebox.showinfo("Успех", "Все тренировки удалены")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()