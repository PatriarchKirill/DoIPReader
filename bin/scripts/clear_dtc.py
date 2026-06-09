import os

# Определяем пути
script_dir = os.path.dirname(os.path.abspath(__file__))  # Папка, где лежит скрипт
cash_diag_path = os.path.normpath(os.path.join(script_dir, "..", "cash", "cash_diag", "cash_diag.txt"))  # Путь к cash_diag.txt

try:
    # Открываем файл в режиме записи ('w' — автоматически очищает файл)
    with open(cash_diag_path, 'w', encoding='utf-8') as file:
        file.write("Clear DTC DONE")  # Записываем текст
    print(f"Файл {cash_diag_path} успешно очищен и обновлён.")
except FileNotFoundError:
    print(f"Ошибка: файл {cash_diag_path} не найден!")
except PermissionError:
    print(f"Ошибка: нет доступа к файлу {cash_diag_path}!")
except Exception as e:
    print(f"Произошла ошибка: {e}")