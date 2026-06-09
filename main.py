import tkinter as tk
import os
import sys
import json
import time
import subprocess
from tkinter import ttk, scrolledtext, messagebox
from threading import Thread

class SVITool:
    def __init__(self, root):
        self.root = root
        self.root.title("SVI TOOL")
        self.root.geometry("1200x700")
        self.root.configure(bg='white')
        self.root.resizable(False, False)
        
        try:
            self.root.iconbitmap('svi.ico')  # Для Windows
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")
            try:
                img = tk.PhotoImage(file='svi.png')
                self.root.tk.call('wm', 'iconphoto', self.root._w, img)
            except Exception as e:
                print(f"Не удалось загрузить иконку в формате PNG: {e}")
        
        self.auto_refresh_active = False
        self.auto_refresh_interval = 1000
        
        self.script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.log_file_path = os.path.join(self.script_dir, "bin", "cash", "cash_diag", "cash_diag.txt")
        self.clear_dtc_script = os.path.join(self.script_dir, "bin", "scripts", "clear_dtc.py")
        self.read_dtc_script = os.path.join(self.script_dir, "bin", "database", "z1_0.py")
        self.status_file = os.path.join(self.script_dir, "bin", "cash", "cash_diag", "connection_status.json")
        self.communicator_script = os.path.join(self.script_dir, "bin", "scripts", "doip_communicator.py")
        
        self.vin = "none"
        self.connection_status = "Disconnected"
        self.auto_refresh_active = False
        
        self.create_info_labels()
        self.create_widgets()
        self.show_home()
        
        self.status_monitor_active = True
        self.status_thread = Thread(target=self.monitor_status)
        self.status_thread.daemon = True
        self.status_thread.start()
        
        self.start_doip_communicator()

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
                   f'Версия: 1.0.0\n' +
                   f'Издатель: SVI\n' +
                   f'Год: 2025\n' +
                   f'Последнее обновление: ---\n' +
                   f'Модельный ряд: Zeekr 001(d)\n\n' +
                   'будет дополняться...')
        text.config(state='disabled')

    def show_diag(self):
        self.clear_frame()
        
        cleardtc_btn = ttk.Button(self.content_frame, text="Clear DTC", command=self.clear_dtc)
        cleardtc_btn.place(x=0, y=0, width=100, height=25)
        
        readdtc_btn = ttk.Button(self.content_frame, text="Read DTC", command=self.read_dtc)
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
                                      mode="determinate")
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

    def auto_refresh_log(self):
        if self.auto_refresh_active:
            self.load_log_file()
            self.root.after(self.auto_refresh_interval, self.auto_refresh_log)

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
            with open(self.log_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_viewer.config(state='normal')
                self.text_viewer.delete(1.0, tk.END)
                self.text_viewer.insert(tk.END, content)
                self.text_viewer.config(state='disabled')
                self.text_viewer.yview(tk.END)
        except FileNotFoundError:
            self.text_viewer.config(state='normal')
            self.text_viewer.delete(1.0, tk.END)
            self.text_viewer.insert(tk.END, f"Файл не найден:\n{self.log_file_path}")
            self.text_viewer.config(state='disabled')
        except Exception as e:
            self.text_viewer.config(state='normal')
            self.text_viewer.delete(1.0, tk.END)
            self.text_viewer.insert(tk.END, f"Ошибка при чтении файла:\n{str(e)}")
            self.text_viewer.config(state='disabled')

    def clear_dtc(self):
        try:
            if not os.path.exists(self.clear_dtc_script):
                messagebox.showerror("Ошибка", f"Файл скрипта не найден:\n{self.clear_dtc_script}")
                return
            
            result = subprocess.run(
                [sys.executable, self.clear_dtc_script],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                messagebox.showinfo("Успех", "DTC успешно очищены")
                self.load_log_file()
            else:
                messagebox.showerror("Ошибка", f"Ошибка при выполнении скрипта:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить скрипт:\n{str(e)}")

    def read_dtc(self):
        try:
            if not os.path.exists(self.read_dtc_script):
                return
            
            subprocess.run(
                [sys.executable, self.read_dtc_script],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
        except Exception as e:
            print(f"Error reading DTC: {e}")

    def start_doip_communicator(self):
        """Запуск DoIP communicator"""
        try:
            if os.path.exists(self.communicator_script):
                subprocess.Popen([sys.executable, self.communicator_script])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start DoIP communicator: {str(e)}")

    def load_status(self):
        """Загрузка статуса из файла"""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    data = json.load(f)
                    self.vin = data.get("vin", "none")
                    self.connection_status = data.get("connection_status", "Disconnected")
        except Exception as e:
            print(f"Error loading status: {e}")

    def monitor_status(self):
        """Мониторинг изменений статуса"""
        while self.status_monitor_active:
            try:
                previous_vin = self.vin
                previous_status = self.connection_status
                
                self.load_status()
                
                if self.vin != previous_vin or self.connection_status != previous_status:
                    self.root.after(0, self.update_status_display)
                
                time.sleep(0.5)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(1)

    def update_status_display(self):
        """Обновление отображения статуса"""
        self.vin_value.config(text=self.vin)
        
        if self.connection_status == "Connected":
            self.connection_value.config(text="Connected", foreground="green")
        else:
            self.connection_value.config(text="Disconnected", foreground="red")

    def show_workshop(self):
        self.clear_frame()
        label = ttk.Label(self.content_frame, text="Workshop", font=('Arial', 16))
        label.pack(pady=20)
        
        ttk.Checkbutton(self.content_frame, text="Включить звук").pack()
        ttk.Checkbutton(self.content_frame, text="Темная тема").pack()

    def show_developer(self):
        self.clear_frame()
        label = ttk.Label(self.content_frame, text="Developer", font=('Arial', 16))
        label.pack(pady=20)
        
        ttk.Label(self.content_frame, text="Имя:").pack()
        ttk.Entry(self.content_frame).pack()
        ttk.Button(self.content_frame, text="Сохранить").pack(pady=10)

    def show_adb(self):
        self.clear_frame()
        label = ttk.Label(self.content_frame, text="ADB", font=('Arial', 16))
        label.pack(pady=20)
        
        ttk.Label(self.content_frame, text="Команда:").pack()
        ttk.Entry(self.content_frame).pack()
        ttk.Button(self.content_frame, text="Выполнить").pack(pady=10)

    def show_upgrade(self):
        self.clear_frame()
        label = ttk.Label(self.content_frame, text="Upgrade OS", font=('Arial', 16))
        label.pack(pady=20)
        
        ttk.Label(self.content_frame, text="Версия:").pack()
        ttk.Entry(self.content_frame).pack()
        ttk.Button(self.content_frame, text="Обновить").pack(pady=10)

    def show_profile(self):
        self.clear_frame()
        label = ttk.Label(self.content_frame, text="Profile", font=('Arial', 16))
        label.pack(pady=20)
        
        ttk.Label(self.content_frame, text="Имя:").pack()
        ttk.Entry(self.content_frame).pack()
        ttk.Button(self.content_frame, text="Сохранить").pack(pady=10)

    def __del__(self):
        self.status_monitor_active = False
        if hasattr(self, 'status_thread') and self.status_thread.is_alive():
            self.status_thread.join()

if __name__ == "__main__":
    root = tk.Tk()
    app = SVITool(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.__del__(), root.destroy()))
    root.mainloop()