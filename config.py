# config.py
import os
import sys

class Config:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # Пути к файлам
        self.log_file_path = os.path.join(self.script_dir, "bin", "cash", "cash_diag", "cash_diag.txt")
        self.clear_dtc_script = os.path.join(self.script_dir, "bin", "scripts", "clear_dtc.py")
        self.read_dtc_script = os.path.join(self.script_dir, "bin", "database", "z1_0.py")
        self.status_file = os.path.join(self.script_dir, "bin", "cash", "cash_diag", "connection_status.json")
        self.communicator_script = os.path.join(self.script_dir, "bin", "scripts", "doip_communicator.py")
        
        # Пути для Developer раздела
        self.dev_build_file = os.path.join(self.script_dir, "bin", "cash", "cash_dev", "cash_dev_build.txt")
        self.dev_info_file = os.path.join(self.script_dir, "bin", "database", "info_dev", "info_dev.txt")
        self.dev_console_file = os.path.join(self.script_dir, "bin", "cash", "cash_dev", "cash_dev_console.txt")
        
        # Пути для Upgrade OS
        self.upgrade_file = os.path.join(self.script_dir, "bin", "cash", "cash_upgrade", "cash_upgrade.txt")
        self.upgrade_script = os.path.join(self.script_dir, "bin", "scripts", "upgradeos_revers.py")
        
        # DoIP настройки
        self.doip_ip = "169.254.19.1"
        self.doip_port = 13400
        
        # Интервалы
        self.auto_refresh_interval = 1000  # мс
        self.status_update_interval = 500  # мс
        
    def ensure_directories(self):
        """Создаёт необходимые директории"""
        dirs = [
            os.path.join(self.script_dir, "bin", "cash", "cash_diag"),
            os.path.join(self.script_dir, "bin", "cash", "cash_dev"),
            os.path.join(self.script_dir, "bin", "cash", "cash_upgrade"),
            os.path.join(self.script_dir, "bin", "database", "info_dev"),
            os.path.join(self.script_dir, "logs")
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)

config = Config()