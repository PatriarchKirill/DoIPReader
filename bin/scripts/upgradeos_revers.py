import os
from datetime import datetime

def main():
    # Пути к файлам (можно изменить)
    input_path = os.path.join('bin', 'cash', 'cash_upgrade', 'work_upb', 'abup_log.txt')
    output_path = os.path.join('bin', 'cash', 'cash_upgrade', 'cash_upgrade.txt')
    
    # Проверяем существование входного файла
    if not os.path.exists(input_path):
        print(f"ОШИБКА: Файл не найден: {input_path}")
        print("Проверьте путь и наличие файла abup_log.txt")
        return
    
    # Создаем папки для выходного файла, если их нет
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        # Читаем исходный файл
        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Обрабатываем строки
        processed_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith('false|'):
                continue
            
            # Простая обработка и перевод
            if 'ScreenReceiver: onReceive: action=android.intent.action.SCREEN_OFF' in line:
                time = ' '.join(line.split()[:2])
                processed_lines.append(f"[Выключение экрана] {time}")
            elif 'Downloader: pauseDownload: no downloading task, do nothing' in line:
                time = ' '.join(line.split()[:2])
                processed_lines.append(f"[Пауза загрузки] {time} - Нет активных задач")
            elif 'App: onCreate()' in line:
                processed_lines.append("[Запуск приложения]")
        
        # Записываем результат
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Обработанный лог от {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n")
            f.write("\n".join(processed_lines))
        
        print("="*50)
        print(f"УСПЕШНО! Лог обработан и сохранен в:")
        print(output_path)
        print(f"Обработано строк: {len(processed_lines)}")
        print("="*50)
    
    except Exception as e:
        print("="*50)
        print(f"ОШИБКА: {e}")
        print("="*50)
        # Записываем ошибку в файл
        error_path = os.path.join(os.path.dirname(output_path), 'error.log')
        with open(error_path, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()}: {e}\n")

if __name__ == "__main__":
    main()