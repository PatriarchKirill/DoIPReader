import os
import time
import subprocess
from threading import Thread

class SystemOptimizer:
    def __init__(self):
        self.scripts_to_monitor = {
            'main': os.path.join(os.path.dirname(__file__), 'main.py'),
            'doip': os.path.join(os.path.dirname(__file__), 'bin', 'scripts', 'doip_communicator.py'),
            'dtc_reader': os.path.join(os.path.dirname(__file__), 'bin', 'database', 'z1_0.py'),
            'dtc_cleaner': os.path.join(os.path.dirname(__file__), 'bin', 'scripts', 'clear_dtc.py')
        }
        self.optimization_interval = 30
        self.running = True

    def start(self):
        """Запуск оптимизатора"""
        print("Starting system optimization (basic mode)...")
        monitor_thread = Thread(target=self.monitor_system)
        monitor_thread.daemon = True
        monitor_thread.start()

    def monitor_system(self):
        """Базовый мониторинг системы"""
        while self.running:
            try:
                self.check_scripts_running()
                self.clean_temp_files()
                time.sleep(self.optimization_interval)
            except Exception as e:
                print(f"Optimization error: {str(e)}")

    def check_scripts_running(self):
        """Проверка работы скриптов"""
        for script_name, script_path in self.scripts_to_monitor.items():
            if not self.is_script_running(script_path):
                print(f"{script_name} is not running, attempting to start...")
                self.start_script(script_path)

    def is_script_running(self, script_path):
        """Проверка работает ли скрипт (базовый метод)"""
        try:
            # Для Windows
            if os.name == 'nt':
                cmd = f'tasklist /FI "IMAGENAME eq python.exe"'
                output = subprocess.check_output(cmd, shell=True).decode()
                return script_path in output
            # Для Linux/Mac
            else:
                cmd = f'ps aux | grep python'
                output = subprocess.check_output(cmd, shell=True).decode()
                return script_path in output
        except Exception:
            return False

    def start_script(self, script_path):
        """Запуск скрипта"""
        try:
            subprocess.Popen(['python', script_path], 
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           start_new_session=True)
            print(f"Successfully started {os.path.basename(script_path)}")
        except Exception as e:
            print(f"Failed to start {os.path.basename(script_path)}: {str(e)}")

    def clean_temp_files(self):
        """Очистка временных файлов"""
        temp_dirs = [
            os.path.join(os.path.dirname(__file__), 'bin', 'cash', 'temp'),
            os.path.join(os.path.dirname(__file__), 'bin', 'cash', 'cache')
        ]
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                            print(f"Cleaned: {file_path}")
                    except Exception as e:
                        print(f"Failed to clean {file_path}: {str(e)}")

    def stop(self):
        """Остановка оптимизатора"""
        self.running = False
        print("System optimizer stopped")

if __name__ == "__main__":
    optimizer = SystemOptimizer()
    try:
        optimizer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        optimizer.stop()