import socket
import time
import os
from datetime import datetime
from binascii import hexlify, unhexlify

# Конфигурация
DOIP_IP = "169.254.19.1"  # Адрес автомобиля из лога
DOIP_PORT = 13400
LOCAL_PORT = 13400
BUFFER_SIZE = 4096
LOG_PATH = r"bin\cash\cash_diag\cash_diag.txt"

# Шаблоны сообщений
VEHICLE_ANNOUNCEMENT = "02FD0004"
DIAGNOSTIC_SESSION_REQUEST = "02FD8001000000021001"  # Default session
EXTENDED_SESSION_REQUEST = "02FD8001000000021003"    # Extended session
READ_DTC_REQUEST = "02FD8001000000021902"            # Read DTCs
READ_ECU_ID_REQUEST = "02FD80010000000322F190"       # Read ECU ID (0xF190)
KEEP_ALIVE = "02FD8001000000013E"                    # Tester present

class DoIPLogger:
    @staticmethod
    def clear_log():
        """Очистка лог-файла"""
        try:
            with open(LOG_PATH, 'w') as f:
                f.write("")
        except Exception as e:
            print(f"Log clear error: {str(e)}")

    @staticmethod
    def log(action, response=None, error=None):
        """Запись в лог-файл"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {action}\n"
        
        if response:
            log_entry += f"    Response: {hexlify(response).decode().upper()}\n"
        if error:
            log_entry += f"    ERROR: {str(error)}\n"
        
        try:
            with open(LOG_PATH, 'a') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Log write error: {str(e)}")

class DoIPDecoder:
    @staticmethod
    def parse_vehicle_announcement(data):
        """Разбор Vehicle Announcement"""
        try:
            return {
                'vin': data[8:25].decode('ascii'),
                'logical_address': f"0x{int.from_bytes(data[25:27], 'big'):04X}"
            }
        except Exception as e:
            DoIPLogger.log("Failed to parse Vehicle Announcement", error=e)
            return None

    @staticmethod
    def parse_dtc_response(data):
        """Разбор ответа с DTC"""
        try:
            if len(data) < 6 or data[0] != 0x59:
                return None
            dtc_count = data[1]
            dtcs = []
            for i in range(dtc_count):
                offset = 2 + i*4
                dtc = f"{data[offset]:02X}{data[offset+1]:02X}{data[offset+2]:02X}"
                dtcs.append(dtc)
            return dtcs
        except Exception as e:
            DoIPLogger.log("Failed to parse DTC response", error=e)
            return None

class DoIPClient:
    def __init__(self):
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind(('0.0.0.0', LOCAL_PORT))
        self.udp_sock.settimeout(5)
        self.tcp_sock = None
        self.ecu_info = None
        DoIPLogger.clear_log()

    def receive_udp_message(self):
        """Получение Vehicle Announcement"""
        DoIPLogger.log("Waiting for Vehicle Announcement...")
        try:
            data, _ = self.udp_sock.recvfrom(BUFFER_SIZE)
            DoIPLogger.log("Received UDP message", response=data)
            
            if hexlify(data[:4]).decode().upper() == VEHICLE_ANNOUNCEMENT:
                self.ecu_info = DoIPDecoder.parse_vehicle_announcement(data)
                if self.ecu_info:
                    DoIPLogger.log(f"Vehicle identified - VIN: {self.ecu_info['vin']}, Address: {self.ecu_info['logical_address']}")
                    return True
            return False
        except socket.timeout:
            DoIPLogger.log("Timeout waiting for Vehicle Announcement", error="No response received")
            return False

    def establish_tcp_connection(self):
        """Установка TCP-соединения"""
        try:
            self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_sock.connect((DOIP_IP, DOIP_PORT))
            DoIPLogger.log("TCP connection established")
            return True
        except Exception as e:
            DoIPLogger.log("Failed to establish TCP connection", error=e)
            return False

    def send_request(self, request_hex, description):
        """Отправка запроса и получение ответа"""
        try:
            request = unhexlify(request_hex)
            self.tcp_sock.sendall(request)
            DoIPLogger.log(f"Sent: {description}", response=request)
            
            response = self.tcp_sock.recv(BUFFER_SIZE)
            DoIPLogger.log(f"Received response for {description}", response=response)
            return response
        except Exception as e:
            DoIPLogger.log(f"Failed to process {description}", error=e)
            return None

    def diagnostic_sequence(self):
        """Основная диагностическая последовательность"""
        # 1. Vehicle Announcement
        if not self.receive_udp_message():
            return

        # 2. TCP подключение
        if not self.establish_tcp_connection():
            return

        # 3. Диагностическая сессия
        session_response = self.send_request(DIAGNOSTIC_SESSION_REQUEST, "Start default session")
        if not session_response or session_response[5] != 0x50:  # Проверка положительного ответа
            DoIPLogger.log("Failed to start diagnostic session")
            return

        # 4. Расширенная сессия (если требуется)
        ext_session_response = self.send_request(EXTENDED_SESSION_REQUEST, "Start extended session")
        
        # 5. Чтение DTC
        dtc_response = self.send_request(READ_DTC_REQUEST, "Read DTCs")
        if dtc_response:
            dtcs = DoIPDecoder.parse_dtc_response(dtc_response[5:])  # Пропускаем DoIP заголовок
            if dtcs:
                DoIPLogger.log(f"Found DTCs: {', '.join(dtcs)}")

        # 6. Чтение идентификатора ECU
        ecu_id_response = self.send_request(READ_ECU_ID_REQUEST, "Read ECU ID")
        
        # 7. Поддержание сессии
        for _ in range(3):  # 3 keep-alive сообщения
            self.send_request(KEEP_ALIVE, "Tester present")
            time.sleep(1)

    def close(self):
        """Закрытие соединений"""
        if self.tcp_sock:
            self.tcp_sock.close()
        self.udp_sock.close()
        DoIPLogger.log("All connections closed")

if __name__ == "__main__":
    client = DoIPClient()
    try:
        client.diagnostic_sequence()
    except Exception as e:
        DoIPLogger.log("Critical error in diagnostic sequence", error=e)
    finally:
        client.close()