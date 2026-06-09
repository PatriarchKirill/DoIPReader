# svi_tool.py (обновленная версия 3.py)
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import sys
import json
import time
import subprocess
import shutil
from threading import Thread
from config import config
from logger import app_logger
from doip_client import doip_client

class SVITool:
    def __init__(self, root):
        self.root = root
        self.root.title("SVI TOOL")
        self.root.geometry("1200x700")
        self.root.configure(bg='white')
        self.root.resizable(False, False)
        
        # Загружаем конфигурацию
        config.ensure_directories()
        
        try:
            self.root.iconbitmap('svi.ico')
        except:
            try:
                img = tk.PhotoImage(file='svi.png')
                self.root.tk.call('wm', 'iconphoto', self.root._w, img)
            except:
                app_logger.warning("Icon not found")
        
        self.auto_refresh_active = False
        
        # Инициализация переменных
        self.vin = "none"
        self.connection_status = "Disconnected"
        
        # Создаем интерфейс
        self.create_info_labels()
        self.create_widgets()
        self.show_home()
        
        # Настройка DoIP клиента
        doip_client.set_status_callback(self.update_status_display)
        doip_client.start()
        
        # Запускаем автообновление статуса (через after вместо потока)
        self.update_status_from_file()
        
        app_logger.info("SVI Tool started successfully")
    
    def create_info_labels(self):
        style = ttk.Style()
        style.configure('White.TLabel', background='white')
        
        ttk.Label(self.root, text="VIN", font=("Arial", 14), foreground="grey", 
                 style='White.TLabel').place(x=160, y=0)
        self.vin_value = ttk.Label(self.root, text=self.vin, font=("Arial", 12), style='White.TLabel')
        self.vin_value.place(x=160, y=25)
        
        ttk.Label(self.root, text="Model/Year", font=("Arial", 14), 
                 foreground="grey", style='White.TLabel').place(x=350, y=0)
        self.model_value = ttk.Label(self.root, text="Zeekr 001", font=("Arial", 12), style='White.TLabel')
        self.model_value.place(x=350, y=25)
        
        ttk.Label(self.root, text="Voltage", font=("Arial", 14), 
                 foreground="grey", style='White.TLabel').place(x=650, y=0)
        self.voltage_value = ttk.Label(self.root, text="13.2V", font=("Arial", 12), style='White.TLabel')
        self.voltage_value.place(x=650, y=25)
        
        ttk.Label(self.root, text="Connection", font=("Arial", 14), 
                 foreground="grey", style='White.TLabel').place(x=860, y=0)
        self.connection_value = ttk.Label(self.root, text=self.connection_status, 
                                        font=("Arial", 12), 
                                        foreground="red", 
                                        style='White.TLabel')
        self.connection_value.place(x=860, y=25)
    
    def create_widgets(self):
        self.content_frame = ttk.Frame(self.root, relief="solid", borderwidth=2)
        self.content_frame.place(x=155, y=60, width=1040, height=620)
        
        buttons = [
            ("Diagnostic", self.show_diag, 3, 60),
            ("Workshop", self.show_workshop, 3, 100),
            ("Developer", self.show_developer, 3, 140),
            ("ADB", self.show_adb, 3, 180),
            ("Upgrade OS", self.show_upgrade, 3, 220),
            ("Profile", self.show_profile, 3, 260)
        ]
        
        for text, command, x, y in buttons:
            button = ttk.Button(self.root, text=text, command=command)
            button.place(x=x, y=y, width=150, height=35)
    
    def clear_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_home(self):
        self.clear_frame()
        
        scrollbar = ttk.Scrollbar(self.content_frame)
        scrollbar.pack(side='right', fill='y')
        
        text = tk.Text(self.content_frame, 
                     wrap='word',
                     yscrollcommand=scrollbar.set,
                     font=('Arial', 10),
                     padx=5, pady=5)
        text.pack(side='left', fill='both', expand=True)
        
        scrollbar.config(command=text.yview)
        text.insert('1.0', 'Информация о софте:\n\n' + 
                   f'Версия: 2.0.0\n' +
                   f'Издатель: SVI\n' +
                   f'Год: 2025\n' +
                   f'Последнее обновление: 2026-04-07\n' +
                   f'Модельный ряд: Zeekr 001(d)\n\n' +
                   'Улучшения в версии 2.0:\n' +
                   '- Неблокирующие операции\n' +
                   '- Улучшенный DoIP клиент\n' +
                   '- Система логирования\n' +
                   '- Оптимизация производительности\n\n' +
                   'будет дополняться...')
        text.config(state='disabled')
    
    def update_status_from_file(self):
        """Обновление статуса из файла (неблокирующее)"""
        try:
            if os.path.exists(config.status_file):
                with open(config.status_file, 'r') as f:
                    data = json.load(f)
                    self.vin = data.get("vin", "none")
                    self.connection_status = data.get("connection_status", "Disconnected")
                    self.update_status_display(self.connection_status, self.vin)
        except Exception as e:
            app_logger.error(f"Status update error: {e}")
        
        # Планируем следующее обновление
        self.root.after(500, self.update_status_from_file)
    
    def update_status_display(self, status, vin=None):
        """Обновление отображения статуса"""
        if vin:
            self.vin_value.config(text=vin)
        
        if status == "Connected":
            self.connection_value.config(text="Connected", foreground="green")
        else:
            self.connection_value.config(text="Disconnected", foreground="red")
    
    def show_diag(self):
        self.clear_frame()
        
        cleardtc_btn = ttk.Button(self.content_frame, text="Clear DTC", command=self.clear_dtc_async)
        cleardtc_btn.place(x=0, y=0, width=100, height=25)
        
        readdtc_btn = ttk.Button(self.content_frame, text="Read DTC", command=self.read_dtc_async)
        readdtc_btn.place(x=100, y=0, width=100, height=25)
        
        rsm_btn = ttk.Button(self.content_frame, text="Restart session")
        rsm_btn.place(x=200, y=0, width=120, height=25)
        
        epm_btn = ttk.Button(self.content_frame, text="Programming Mode")
        epm_btn.place(x=320, y=0, width=160, height=25)
        
        reset_btn = ttk.Button(self.content_frame, text="Start LOG", command=self.start_auto_refresh)
        reset_btn.place(x=480, y=0, width=100, height=25)
        
        refresh_btn = ttk.Button(self.content_frame, text="Stop LOG", command=self.stop_auto_refresh)
        refresh_btn.place(x=580, y=0, width=100, height=25)
        
        progress_frame = ttk.Frame(self.content_frame)
        progress_frame.pack(side='bottom', fill='x', pady=0)
        
        self.progress = ttk.Progressbar(progress_frame, 
                                      orient="horizontal",
                                      length=1000,
                                      mode="indeterminate")
        self.progress.pack(pady=10)
        
        text_frame = ttk.Frame(self.content_frame)
        text_frame.pack(fill='both', expand=True, pady=(30, 0))
        
        self.text_viewer = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=('Courier New', 10),
            state='disabled'
        )
        self.text_viewer.pack(fill='both', expand=True)
        
        self.load_log_file()
    
    def clear_dtc_async(self):
        """Асинхронная очистка DTC"""
        self.progress.start()
        Thread(target=self._clear_dtc_worker, daemon=True).start()
    
    def _clear_dtc_worker(self):
        """Рабочий поток для очистки DTC"""
        try:
            # Используем DoIP клиент если он подключен
            if doip_client.status == "Connected":
                success = doip_client.clear_dtc()
                if success:
                    self.root.after(0, lambda: messagebox.showinfo("Успех", "DTC успешно очищены"))
                    self.root.after(0, self.load_log_file)
                else:
                    self.root.after(0, lambda: messagebox.showerror("Ошибка", "Не удалось очистить DTC"))
            else:
                # Fallback на старый скрипт
                if os.path.exists(config.clear_dtc_script):
                    result = subprocess.run(
                        [sys.executable, config.clear_dtc_script],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        self.root.after(0, lambda: messagebox.showinfo("Успех", "DTC успешно очищены"))
                        self.root.after(0, self.load_log_file)
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Ошибка", result.stderr))
        except Exception as e:
            app_logger.error(f"Clear DTC error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Ошибка", str(e)))
        finally:
            self.root.after(0, self.progress.stop)
    
    def read_dtc_async(self):
        """Асинхронное чтение DTC"""
        self.progress.start()
        Thread(target=self._read_dtc_worker, daemon=True).start()
    
    def _read_dtc_worker(self):
        """Рабочий поток для чтения DTC"""
        try:
            if doip_client.status == "Connected":
                dtc_data = doip_client.read_dtc()
                if dtc_data:
                    app_logger.info(f"DTC data: {dtc_data}")
                    self.root.after(0, lambda: messagebox.showinfo("DTC", f"DTC прочитаны:\n{dtc_data}"))
                else:
                    self.root.after(0, lambda: messagebox.showinfo("DTC", "DTC не найдены"))
            else:
                if os.path.exists(config.read_dtc_script):
                    subprocess.Popen([sys.executable, config.read_dtc_script])
        except Exception as e:
            app_logger.error(f"Read DTC error: {e}")
        finally:
            self.root.after(0, self.progress.stop)
    
    def auto_refresh_log(self):
        if self.auto_refresh_active:
            self.load_log_file()
            self.root.after(config.auto_refresh_interval, self.auto_refresh_log)
    
    def start_auto_refresh(self):
        if not self.auto_refresh_active:
            self.auto_refresh_active = True
            self.auto_refresh_log()
            messagebox.showinfo("Автообновление", "Автообновление лога запущено")
    
    def stop_auto_refresh(self):
        if self.auto_refresh_active:
            self.auto_refresh_active = False
            messagebox.showinfo("Автообновление", "Автообновление лога остановлено")
    
    def load_log_file(self):
        try:
            with open(config.log_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_viewer.config(state='normal')
                self.text_viewer.delete(1.0, tk.END)
                self.text_viewer.insert(tk.END, content)
                self.text_viewer.config(state='disabled')
                self.text_viewer.yview(tk.END)
        except FileNotFoundError:
            self.text_viewer.config(state='normal')
            self.text_viewer.delete(1.0, tk.END)
            self.text_viewer.insert(tk.END, f"Файл не найден:\n{config.log_file_path}")
            self.text_viewer.config(state='disabled')
        except Exception as e:
            app_logger.error(f"Load log error: {e}")
            self.text_viewer.config(state='normal')
            self.text_viewer.delete(1.0, tk.END)
            self.text_viewer.insert(tk.END, f"Ошибка при чтении файла:\n{str(e)}")
            self.text_viewer.config(state='disabled')
    
    def show_workshop(self):
        self.clear_frame()
        label = ttk.Label(self.content_frame, text="Workshop", font=('Arial', 16))
        label.pack(pady=20)
        
        self.sound_var = tk.BooleanVar()
        self.theme_var = tk.BooleanVar()
        
        ttk.Checkbutton(self.content_frame, text="Включить звук", variable=self.sound_var).pack()
        ttk.Checkbutton(self.content_frame, text="Темная тема", variable=self.theme_var).pack()
        
        ttk.Button(self.content_frame, text="Сохранить настройки", 
                  command=self.save_workshop_settings).pack(pady=10)
    
    def save_workshop_settings(self):
        """Сохранение настроек Workshop"""
        settings = {
            "sound_enabled": self.sound_var.get(),
            "dark_theme": self.theme_var.get()
        }
        try:
            with open(os.path.join(config.script_dir, "workshop_settings.json"), 'w') as f:
                json.dump(settings, f)
            messagebox.showinfo("Успех", "Настройки сохранены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
    
    def show_developer(self):
        self.clear_frame()
        
        # Создаем верхний фрейм для кнопок
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(side='top', fill='x', pady=5)
        
        # Выпадающий список
        self.module_var = tk.StringVar()
        module_combobox = ttk.Combobox(button_frame, 
                                     textvariable=self.module_var,
                                     values=["VCU", "BMS", "MCU"],
                                     state="readonly",
                                     width=10)
        module_combobox.current(0)
        module_combobox.pack(side='left', padx=5)
        module_combobox.bind('<<ComboboxSelected>>', self.on_module_selected)
        
        # Кнопки управления
        ttk.Button(button_frame, text="Load/Install", command=self.load_install).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Load As", command=self.load_as).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Extract", command=self.extract).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Сохранить", command=self.save_dev_build_file).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Обновить", command=self.update_dev_files).pack(side='left', padx=5)
        self.split_button = ttk.Button(button_frame, text="Split", command=self.split_frames)
        self.split_button.pack(side='left', padx=5)
        self.unsplit_button = ttk.Button(button_frame, text="Unsplit", command=self.unsplit_frames, state='disabled')
        self.unsplit_button.pack(side='left', padx=5)
        
        # Контейнер для верхних фреймов
        self.dual_frame_container = ttk.Frame(self.content_frame)
        self.dual_frame_container.pack(side='top', fill='both', expand=True)
        
        # Frame 1 (редактируемый)
        self.frame1 = ttk.Frame(self.dual_frame_container, relief="solid", borderwidth=1)
        self.frame1.pack(side='left', fill='both', expand=True)
        
        self.dev_build_text = scrolledtext.ScrolledText(
            self.frame1,
            wrap=tk.WORD,
            font=('Courier New', 10),
            state='normal'
        )
        self.dev_build_text.pack(fill='both', expand=True)
        self.load_text_file(config.dev_build_file, self.dev_build_text)
        
        # Frame 2 (только чтение) - изначально скрыт
        self.frame2 = ttk.Frame(self.dual_frame_container, relief="solid", borderwidth=1)
        
        # Frame 3 (консоль, только чтение)
        self.frame3 = ttk.Frame(self.content_frame, relief="solid", borderwidth=1, height=100)
        self.frame3.pack(side='bottom', fill='x', pady=5)
        
        self.dev_console_text = scrolledtext.ScrolledText(
            self.frame3,
            wrap=tk.WORD,
            font=('Courier New', 10),
            state='disabled'
        )
        self.dev_console_text.pack(fill='both', expand=True)
        self.load_text_file(config.dev_console_file, self.dev_console_text)
    
    def on_module_selected(self, event=None):
        """Загрузка информации о выбранном модуле"""
        module = self.module_var.get()
        info_files = {
            "VCU": "info_vcu.txt",
            "BMS": "info_bms.txt", 
            "MCU": "info_mcu.txt"
        }
        
        if module in info_files:
            info_path = os.path.join(config.script_dir, "bin", "database", info_files[module])
            if hasattr(self, 'dev_info_text') and self.dev_info_text:
                self.load_text_file(info_path, self.dev_info_text)
    
    def load_install(self):
        """Обработчик кнопки Load/Install"""
        selected_module = self.module_var.get()
        if doip_client.status == "Connected":
            messagebox.showinfo("Load/Install", f"Загрузка/установка для модуля: {selected_module}\nПодключение к автомобилю установлено")
            # Здесь будет реальная логика прошивки
        else:
            messagebox.showwarning("Внимание", "Нет подключения к автомобилю")
    
    def load_as(self):
        """Обработчик кнопки Load As"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.dev_build_text.config(state='normal')
                    self.dev_build_text.delete(1.0, tk.END)
                    self.dev_build_text.insert(tk.END, content)
                    messagebox.showinfo("Успех", "Файл успешно загружен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def extract(self):
        """Обработчик кнопки Extract"""
        selected_module = self.module_var.get()
        if doip_client.status == "Connected":
            messagebox.showinfo("Extract", f"Извлечение данных для модуля: {selected_module}\nЧтение данных из автомобиля...")
            # Здесь будет реальная логика извлечения данных
        else:
            messagebox.showwarning("Внимание", "Нет подключения к автомобилю")
    
    def split_frames(self):
        """Показывает второй фрейм"""
        if not self.frame2.winfo_ismapped():
            self.frame2.pack(side='left', fill='both', expand=True)
            
            self.dev_info_text = scrolledtext.ScrolledText(
                self.frame2,
                wrap=tk.WORD,
                font=('Courier New', 10),
                state='disabled'
            )
            self.dev_info_text.pack(fill='both', expand=True)
            
            # Загружаем информацию о текущем модуле
            self.on_module_selected()
            
            self.split_button.config(state='disabled')
            self.unsplit_button.config(state='normal')
    
    def unsplit_frames(self):
        """Скрывает второй фрейм"""
        if self.frame2.winfo_ismapped():
            self.frame2.pack_forget()
            for widget in self.frame2.winfo_children():
                widget.destroy()
            self.dev_info_text = None
            
            self.split_button.config(state='normal')
            self.unsplit_button.config(state='disabled')
    
    def load_text_file(self, file_path, text_widget):
        """Загружает файл в текстовое поле"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                current_state = text_widget['state']
                text_widget.config(state='normal')
                text_widget.delete(1.0, tk.END)
                text_widget.insert(tk.END, content)
                text_widget.config(state=current_state)
                text_widget.yview(tk.END)
        except FileNotFoundError:
            current_state = text_widget['state']
            text_widget.config(state='normal')
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"Файл не найден:\n{file_path}")
            text_widget.config(state=current_state)
        except Exception as e:
            app_logger.error(f"Load text file error: {e}")
            current_state = text_widget['state']
            text_widget.config(state='normal')
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"Ошибка при чтении файла:\n{str(e)}")
            text_widget.config(state=current_state)
    
    def save_dev_build_file(self):
        """Сохраняет изменения из редактируемого текстового поля в файл"""
        try:
            content = self.dev_build_text.get(1.0, tk.END)
            with open(config.dev_build_file, 'w', encoding='utf-8') as file:
                file.write(content)
            messagebox.showinfo("Успех", "Файл успешно сохранен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
    
    def update_dev_files(self):
        """Обновляет содержимое всех текстовых виджетов"""
        self.load_text_file(config.dev_build_file, self.dev_build_text)
        if hasattr(self, 'dev_info_text') and self.dev_info_text and self.frame2.winfo_ismapped():
            self.load_text_file(config.dev_info_file, self.dev_info_text)
        self.load_text_file(config.dev_console_file, self.dev_console_text)
        messagebox.showinfo("Обновление", "Содержимое файлов обновлено")
    
    def show_adb(self):
        self.clear_frame()
        
        label = ttk.Label(self.content_frame, text="ADB", font=('Arial', 16))
        label.pack(pady=20)
        
        # Фрейм для ввода команды
        cmd_frame = ttk.Frame(self.content_frame)
        cmd_frame.pack(pady=10)
        
        ttk.Label(cmd_frame, text="Команда:").pack(side='left', padx=5)
        self.adb_cmd_entry = ttk.Entry(cmd_frame, width=50)
        self.adb_cmd_entry.pack(side='left', padx=5)
        ttk.Button(cmd_frame, text="Выполнить", command=self.execute_adb_command).pack(side='left', padx=5)
        
        # Кнопки быстрых команд
        quick_frame = ttk.Frame(self.content_frame)
        quick_frame.pack(pady=10)
        
        ttk.Button(quick_frame, text="adb devices", 
                  command=lambda: self.execute_quick_adb("devices")).pack(side='left', padx=5)
        ttk.Button(quick_frame, text="adb reboot", 
                  command=lambda: self.execute_quick_adb("reboot")).pack(side='left', padx=5)
        ttk.Button(quick_frame, text="adb logcat", 
                  command=lambda: self.execute_quick_adb("logcat")).pack(side='left', padx=5)
        
        # Текстовое поле для вывода
        self.adb_output = scrolledtext.ScrolledText(
            self.content_frame,
            wrap=tk.WORD,
            font=('Courier New', 10),
            height=20
        )
        self.adb_output.pack(fill='both', expand=True, pady=10)
    
    def execute_adb_command(self):
        """Выполнение ADB команды"""
        command = self.adb_cmd_entry.get().strip()
        if command:
            Thread(target=self._run_adb_command, args=(command,), daemon=True).start()
    
    def execute_quick_adb(self, subcommand):
        """Выполнение быстрой ADB команды"""
        Thread(target=self._run_adb_command, args=(subcommand,), daemon=True).start()
    
    def _run_adb_command(self, command):
        """Запуск ADB команды в отдельном потоке"""
        try:
            result = subprocess.run(
                f"adb {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = f"$ adb {command}\n"
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"ERROR: {result.stderr}\n"
            output += "\n"
            
            self.root.after(0, lambda: self.adb_output.insert(tk.END, output))
            self.root.after(0, lambda: self.adb_output.yview(tk.END))
            
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.adb_output.insert(tk.END, "Command timed out\n\n"))
        except Exception as e:
            self.root.after(0, lambda: self.adb_output.insert(tk.END, f"Error: {str(e)}\n\n"))
    
    def show_upgrade(self):
        self.clear_frame()
        
        # Создаем верхний фрейм для кнопок
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(side='top', fill='x', pady=5)
        
        # Левая группа кнопок
        left_button_frame = ttk.Frame(button_frame)
        left_button_frame.pack(side='left', padx=1)
        
        ttk.Button(left_button_frame, text="Load", command=self.load_upgrade_file).pack(side='left', padx=1)
        ttk.Button(left_button_frame, text="Export", command=self.export_upgrade_file).pack(side='left', padx=1)
        ttk.Button(left_button_frame, text="Start", command=self.start_upgrade_async).pack(side='left', padx=1)
        
        # Правая группа кнопок
        right_button_frame = ttk.Frame(button_frame)
        right_button_frame.pack(side='right', padx=1)
        
        ttk.Button(right_button_frame, text="Real Time Monitoring", 
                  command=self.open_monitoring_window).pack(side='left', padx=1)
        ttk.Button(right_button_frame, text="Start LOG", command=self.start_upgrade_log).pack(side='left', padx=1)
        ttk.Button(right_button_frame, text="Stop LOG", command=self.stop_upgrade_log).pack(side='left', padx=1)
        
        # Текстовый редактор (только для чтения)
        text_frame = ttk.Frame(self.content_frame)
        text_frame.pack(fill='both', expand=True, pady=(5, 0))
        
        self.upgrade_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=('Courier New', 10),
            state='disabled'
        )
        self.upgrade_text.pack(fill='both', expand=True)
        
        # Загружаем содержимое файла
        self.load_upgrade_text(config.upgrade_file)
        
        # Прогресс бар
        progress_frame = ttk.Frame(self.content_frame)
        progress_frame.pack(side='bottom', fill='x', pady=5)
        
        self.upgrade_progress = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=1000,
            mode="determinate"
        )
        self.upgrade_progress.pack(fill='x')
        
        self.upgrade_log_active = False
    
    def load_upgrade_text(self, file_path):
        """Загружает содержимое файла в текстовый редактор"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.upgrade_text.config(state='normal')
                self.upgrade_text.delete(1.0, tk.END)
                self.upgrade_text.insert(tk.END, content)
                self.upgrade_text.config(state='disabled')
                self.upgrade_text.yview(tk.END)
        except FileNotFoundError:
            self.upgrade_text.config(state='normal')
            self.upgrade_text.delete(1.0, tk.END)
            self.upgrade_text.insert(tk.END, f"Файл не найден:\n{file_path}")
            self.upgrade_text.config(state='disabled')
        except Exception as e:
            app_logger.error(f"Load upgrade text error: {e}")
            self.upgrade_text.config(state='normal')
            self.upgrade_text.delete(1.0, tk.END)
            self.upgrade_text.insert(tk.END, f"Ошибка при чтении файла:\n{str(e)}")
            self.upgrade_text.config(state='disabled')
    
    def load_upgrade_file(self):
        """Обработчик кнопки Load"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл abup_log.txt",
            filetypes=[("Log files", "abup_log.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Целевая папка
                target_dir = os.path.join(config.script_dir, "bin", "cash", "cash_upgrade", "work_upb")
                os.makedirs(target_dir, exist_ok=True)
                
                # Копируем файл
                target_path = os.path.join(target_dir, "abup_log.txt")
                shutil.copy(file_path, target_path)
                
                messagebox.showinfo("Успех", f"Файл успешно скопирован в:\n{target_path}")
                
                # Обновляем содержимое текстового редактора
                self.load_upgrade_text(config.upgrade_file)
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def export_upgrade_file(self):
        """Обработчик кнопки Export"""
        if not os.path.exists(config.upgrade_file):
            messagebox.showerror("Ошибка", "Исходный файл не найден")
            return
        
        target_path = filedialog.asksaveasfilename(
            title="Сохранить файл cash_upgrade.txt",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if target_path:
            try:
                shutil.copy(config.upgrade_file, target_path)
                messagebox.showinfo("Успех", f"Файл успешно сохранен в:\n{target_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать файл:\n{str(e)}")
    
    def start_upgrade_async(self):
        """Асинхронный запуск обновления"""
        if not os.path.exists(config.upgrade_script):
            messagebox.showerror("Ошибка", f"Скрипт не найден:\n{config.upgrade_script}")
            return
        
        self.upgrade_progress["value"] = 0
        Thread(target=self._run_upgrade_worker, daemon=True).start()
    
    def _run_upgrade_worker(self):
        """Рабочий поток для обновления"""
        try:
            result = subprocess.run(
                [sys.executable, config.upgrade_script],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.root.after(0, lambda: messagebox.showinfo("Успех", "Обновление завершено успешно"))
                self.root.after(0, lambda: self.load_upgrade_text(config.upgrade_file))
            else:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", result.stderr))
                
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", "Превышено время ожидания"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", str(e)))
        finally:
            self.root.after(0, lambda: self.upgrade_progress.configure(value=0))
    
    def open_monitoring_window(self):
        """Открывает окно мониторинга в реальном времени"""
        monitor_window = tk.Toplevel(self.root)
        monitor_window.title("Real Time Monitoring - Upgrade OS")
        monitor_window.geometry("800x400")
        
        text_widget = scrolledtext.ScrolledText(monitor_window, wrap=tk.WORD, font=('Courier New', 10))
        text_widget.pack(fill='both', expand=True)
        
        def update_monitor():
            if monitor_window.winfo_exists():
                try:
                    if os.path.exists(config.upgrade_file):
                        with open(config.upgrade_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            text_widget.config(state='normal')
                            text_widget.delete(1.0, tk.END)
                            text_widget.insert(tk.END, content)
                            text_widget.config(state='disabled')
                            text_widget.yview(tk.END)
                except Exception as e:
                    pass
                monitor_window.after(1000, update_monitor)
        
        update_monitor()
    
    def start_upgrade_log(self):
        """Запуск записи лога обновления"""
        self.upgrade_log_active = True
        messagebox.showinfo("Лог", "Запись лога обновления запущена")
    
    def stop_upgrade_log(self):
        """Остановка записи лога обновления"""
        self.upgrade_log_active = False
        messagebox.showinfo("Лог", "Запись лога обновления остановлена")
    
    def show_profile(self):
        self.clear_frame()
        label = ttk.Label(self.content_frame, text="Profile", font=('Arial', 16))
        label.pack(pady=20)
        
        # Загрузка сохранённого профиля
        profile_file = os.path.join(config.script_dir, "profile.json")
        profile_data = {}
        if os.path.exists(profile_file):
            try:
                with open(profile_file, 'r') as f:
                    profile_data = json.load(f)
            except:
                pass
        
        # Поля профиля
        ttk.Label(self.content_frame, text="Имя пользователя:").pack()
        self.profile_name = ttk.Entry(self.content_frame, width=30)
        self.profile_name.insert(0, profile_data.get("username", ""))
        self.profile_name.pack(pady=5)
        
        ttk.Label(self.content_frame, text="Email:").pack()
        self.profile_email = ttk.Entry(self.content_frame, width=30)
        self.profile_email.insert(0, profile_data.get("email", ""))
        self.profile_email.pack(pady=5)
        
        ttk.Label(self.content_frame, text="Телефон:").pack()
        self.profile_phone = ttk.Entry(self.content_frame, width=30)
        self.profile_phone.insert(0, profile_data.get("phone", ""))
        self.profile_phone.pack(pady=5)
        
        ttk.Button(self.content_frame, text="Сохранить профиль", 
                  command=self.save_profile).pack(pady=20)
        
        ttk.Button(self.content_frame, text="Загрузить профиль", 
                  command=self.load_profile).pack()
    
    def save_profile(self):
        """Сохранение профиля"""
        profile_data = {
            "username": self.profile_name.get(),
            "email": self.profile_email.get(),
            "phone": self.profile_phone.get(),
            "saved_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(os.path.join(config.script_dir, "profile.json"), 'w') as f:
                json.dump(profile_data, f, indent=2)
            messagebox.showinfo("Успех", "Профиль успешно сохранён")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить профиль: {e}")
    
    def load_profile(self):
        """Загрузка профиля"""
        profile_file = os.path.join(config.script_dir, "profile.json")
        if os.path.exists(profile_file):
            try:
                with open(profile_file, 'r') as f:
                    profile_data = json.load(f)
                    self.profile_name.delete(0, tk.END)
                    self.profile_name.insert(0, profile_data.get("username", ""))
                    self.profile_email.delete(0, tk.END)
                    self.profile_email.insert(0, profile_data.get("email", ""))
                    self.profile_phone.delete(0, tk.END)
                    self.profile_phone.insert(0, profile_data.get("phone", ""))
                messagebox.showinfo("Успех", "Профиль загружен")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить профиль: {e}")
        else:
            messagebox.showwarning("Внимание", "Сохранённый профиль не найден")
    
    def __del__(self):
        doip_client.stop()
        app_logger.info("SVI Tool stopped")

if __name__ == "__main__":
    root = tk.Tk()
    app = SVITool(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.__del__(), root.destroy()))
    root.mainloop()