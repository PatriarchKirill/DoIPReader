# doip_client.py
import socket
import json
import time
import threading
from datetime import datetime
from config import config
from logger import app_logger

class DoIPClient:
    def __init__(self):
        self.running = False
        self.status = "Disconnected"
        self.vin = "none"
        self.udp_sock = None
        self.tcp_sock = None
        self.status_update_callback = None
        
    def set_status_callback(self, callback):
        """Устанавливает callback для обновления статуса в GUI"""
        self.status_update_callback = callback
    
    def update_status(self, status, vin=None):
        """Обновляет статус и сохраняет в JSON"""
        self.status = status
        if vin:
            self.vin = vin
        
        status_data = {
            "connection_status": self.status,
            "vin": self.vin,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(config.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
            
            if self.status_update_callback:
                self.status_update_callback(self.status, self.vin)
                
        except Exception as e:
            app_logger.error(f"Failed to update status: {e}")
    
    def start(self):
        """Запускает DoIP клиент в отдельном потоке"""
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        app_logger.info("DoIP client started")
    
    def stop(self):
        """Останавливает DoIP клиент"""
        self.running = False
        if self.tcp_sock:
            self.tcp_sock.close()
        if self.udp_sock:
            self.udp_sock.close()
        app_logger.info("DoIP client stopped")
    
    def _run(self):
        """Основной цикл DoIP клиента"""
        while self.running:
            try:
                # Попытка подключения
                if self.status != "Connected":
                    self._connect()
                else:
                    # Отправка keep-alive
                    self._send_keep_alive()
                
                time.sleep(2)
            except Exception as e:
                app_logger.error(f"DoIP client error: {e}")
                self.update_status("Disconnected")
    
    def _connect(self):
        """Подключение к автомобилю"""
        try:
            app_logger.info("Attempting to connect to vehicle...")
            
            # UDP для Vehicle Announcement
            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_sock.settimeout(3)
            self.udp_sock.bind(('0.0.0.0', 13400))
            
            # Ждём объявление автомобиля
            data, addr = self.udp_sock.recvfrom(4096)
            
            # Парсим VIN из Vehicle Announcement (упрощённо)
            if len(data) > 8:
                vin = data[8:25].decode('ascii', errors='ignore')
                self.update_status("Connected", vin)
                app_logger.info(f"Connected to vehicle with VIN: {vin}")
                
                # TCP соединение
                self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.tcp_sock.connect((config.doip_ip, config.doip_port))
                app_logger.info("TCP connection established")
            else:
                self.update_status("Disconnected")
                
        except socket.timeout:
            self.update_status("Disconnected")
        except Exception as e:
            app_logger.error(f"Connection error: {e}")
            self.update_status("Disconnected")
        finally:
            if self.udp_sock:
                self.udp_sock.close()
                self.udp_sock = None
    
    def _send_keep_alive(self):
        """Отправка keep-alive сообщения"""
        try:
            if self.tcp_sock:
                # Tester present message (0x3E)
                keep_alive = bytes.fromhex("02 FD 80 01 00 00 00 01 3E")
                self.tcp_sock.sendall(keep_alive)
        except Exception as e:
            app_logger.error(f"Keep-alive failed: {e}")
            self.update_status("Disconnected")
    
    def clear_dtc(self):
        """Очистка DTC"""
        try:
            if self.tcp_sock:
                # Clear DTC command (0x14)
                clear_cmd = bytes.fromhex("02 FD 80 01 00 00 00 02 14 FF FF FF")
                self.tcp_sock.sendall(clear_cmd)
                response = self.tcp_sock.recv(4096)
                return True
        except Exception as e:
            app_logger.error(f"Clear DTC failed: {e}")
        return False
    
    def read_dtc(self):
        """Чтение DTC"""
        try:
            if self.tcp_sock:
                # Read DTC command (0x19 0x02)
                read_cmd = bytes.fromhex("02 FD 80 01 00 00 00 03 19 02 FF")
                self.tcp_sock.sendall(read_cmd)
                response = self.tcp_sock.recv(4096)
                return response.hex()
        except Exception as e:
            app_logger.error(f"Read DTC failed: {e}")
        return None

# Глобальный экземпляр
doip_client = DoIPClient()