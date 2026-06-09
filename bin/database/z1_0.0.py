import socket
import time
import os
from datetime import datetime

# Configuration (Конфигурация)
DOIP_IP = "169.254.19.1"  # IP-адрес автомобиля (Замените на реальный IP)
DOIP_PORT = 13400  # Стандартный порт DoIP
LOG_PATH = r"bin\cash\cash_diag\cash_diag.txt"  # Путь к файлу лога
ECU_LOGICAL_ADDRESS = 0x0E00  # Логический адрес ECU (по умолчанию для двигателя)
KEEP_ALIVE_INTERVAL = 5  # Интервал отправки keep-alive сообщений (в секундах)

# DoIP message templates (Шаблоны DoIP сообщений)
VEHICLE_ID_REQUEST = bytes.fromhex("02 FD 00 01 00 00 00 00")  # Запрос идентификации
EXTENDED_ACCESS_REQUEST = bytes.fromhex("02 FD 00 10 00 00 00 01 01")  # Запрос расширенного доступа
KEEP_ALIVE = bytes.fromhex("02 FD 00 00 00 00 00 01 04")  # Подтверждение связи
ECU_DATA_REQUEST = bytes.fromhex(f"02 FD 00 20 00 00 00 02 {ECU_LOGICAL_ADDRESS:04X}")  # Запрос данных ECU

def clear_log_file():
    """Очищает файл лога перед началом новой сессии"""
    try:
        with open(LOG_PATH, 'w', encoding='utf-8') as f:
            f.write("")
        return True
    except Exception as e:
        print(f"Failed to clear log file: {str(e)}")
        return False

def log_action(action, response=None, error=None):
    """Логирует действия с временной меткой в файл"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action}\n"
    
    if response:
        log_entry += f"    Response: {response.hex().upper()}\n"
    if error:
        log_entry += f"    ERROR: {str(error)}\n"
    
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Failed to write to log file: {str(e)}")

def send_doip_message(sock, message, description):
    """Отправляет DoIP сообщение и логирует действие"""
    try:
        sock.sendall(message)
        log_action(f"Sent: {description}")
        return True
    except Exception as e:
        log_action(f"Failed to send: {description}", error=e)
        return False

def receive_response(sock, timeout=2):
    """Принимает ответ с таймаутом"""
    try:
        sock.settimeout(timeout)
        response = sock.recv(4096)
        return response if response else None
    except socket.timeout:
        return None
    except Exception as e:
        log_action("Error receiving response", error=e)
        return None

def main():
    # Очищаем файл лога
    if not clear_log_file():
        print("Cannot continue without log file access")
        return

    log_action("Starting DoIP communication session")
    
    try:
        # Создаем TCP сокет для DoIP
        log_action("Creating TCP socket for DoIP connection")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        # Подключаемся к автомобилю
        log_action(f"Connecting to {DOIP_IP}:{DOIP_PORT}")
        sock.connect((DOIP_IP, DOIP_PORT))
        log_action("Connection established successfully")
        
        # 1. Запрос расширенного доступа
        if send_doip_message(sock, EXTENDED_ACCESS_REQUEST, "Extended access request"):
            response = receive_response(sock)
            if response:
                log_action("Received response for extended access request", response)
            else:
                log_action("No response received for extended access request")
        
        # 2. Запрос данных ECU
        if send_doip_message(sock, ECU_DATA_REQUEST, "ECU data request"):
            response = receive_response(sock)
            if response:
                log_action("Received response for ECU data request", response)
            else:
                log_action("No response received for ECU data request")
        
        # 3. Цикл подтверждения связи
        log_action("Starting keep-alive loop")
        start_time = time.time()
        while time.time() - start_time < 30:  # 30 секунд работы
            if send_doip_message(sock, KEEP_ALIVE, "Keep-alive message"):
                response = receive_response(sock)
                if response:
                    log_action("Received keep-alive response", response)
                else:
                    log_action("No response for keep-alive")
            
            time.sleep(KEEP_ALIVE_INTERVAL)
        
    except Exception as e:
        log_action("Fatal error in DoIP communication", error=e)
    finally:
        if 'sock' in locals():
            sock.close()
            log_action("Connection closed")
        
        log_action("DoIP communication session ended")

if __name__ == "__main__":
    print("Starting DoIP communication script...")
    main()
    print("Script execution completed")