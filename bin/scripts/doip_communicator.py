import os
import time
import json
from threading import Thread

# Получаем абсолютный путь к файлам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATUS_FILE = os.path.join(BASE_DIR, "bin", "cash", "cash_diag", "connection_status.json")
LOG_FILE = os.path.join(BASE_DIR, "bin", "cash", "cash_diag", "cash_diag.txt")

class DoIPCommunicator:
    def __init__(self):
        self.running = True
        self._ensure_files_exist()
        self.update_status("Disconnected", "none")

    def _ensure_files_exist(self):
        """Создает необходимые файлы, если они не существуют"""
        os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
        if not os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'w') as f:
                json.dump({"status": "Disconnected", "vin": "none"}, f)
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w'): pass

    def update_status(self, status, vin):
        """Обновляет статус соединения"""
        try:
            with open(STATUS_FILE, 'w') as f:
                json.dump({
                    "status": status,
                    "vin": vin,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }, f)
        except Exception as e:
            self.log_error(f"Failed to update status: {str(e)}")

    def log_message(self, message):
        """Логирует сообщение"""
        try:
            with open(LOG_FILE, 'a') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        except Exception as e:
            print(f"Failed to log message: {str(e)}")

    def log_error(self, error):
        """Логирует ошибку"""
        self.log_message(f"ERROR: {error}")

    def connect(self):
        """Имитация подключения к автомобилю"""
        self.log_message("Starting DoIP connection...")
        time.sleep(2)  # Имитация времени подключения
        self.update_status("Connected", "XTA12345678901234")
        self.log_message("Vehicle connected successfully")

    def disconnect(self):
        """Имитация отключения"""
        self.update_status("Disconnected", "none")
        self.log_message("Vehicle disconnected")

    def monitor_connection(self):
        """Мониторинг состояния соединения"""
        while self.running:
            current_status = self.get_current_status()
            
            if current_status["status"] == "Connected":
                # 10% вероятность разрыва соединения для демонстрации
                if time.time() % 10 < 1:
                    self.disconnect()
            else:
                # Попытка переподключения
                self.connect()
            
            time.sleep(2)

    def get_current_status(self):
        """Возвращает текущий статус"""
        default = {"status": "Disconnected", "vin": "none"}
        try:
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return default

    def start(self):
        """Запуск сервиса"""
        self.connect()
        Thread(target=self.monitor_connection, daemon=True).start()

    def stop(self):
        """Остановка сервиса"""
        self.running = False
        self.disconnect()

if __name__ == "__main__":
    communicator = DoIPCommunicator()
    try:
        communicator.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        communicator.stop()