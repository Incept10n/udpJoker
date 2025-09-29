from datetime import datetime, timedelta
import os
import json

# Загрузка данных
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_time(time_str):
    try:
        time_str = time_str.lower().strip()
        
        # "через X минут/часов"
        if 'через' in time_str:
            if 'минут' in time_str:
                minutes = int(''.join(filter(str.isdigit, time_str)))
                return datetime.now() + timedelta(minutes=minutes)
            elif 'час' in time_str:
                hours = int(''.join(filter(str.isdigit, time_str)))
                return datetime.now() + timedelta(hours=hours)
        
        # Просто время "HH:MM"
        elif ':' in time_str and len(time_str.split()) == 1:
            hours, minutes = map(int, time_str.split(':'))
            notification_time = datetime.now().replace(hour=hours, minute=minutes, second=0, microsecond=0)
            if notification_time < datetime.now():
                notification_time += timedelta(days=1)
            return notification_time
        
        # Время с датой "HH:MM DD.MM"
        elif ':' in time_str and len(time_str.split()) == 2:
            time_part, date_part = time_str.split()
            hours, minutes = map(int, time_part.split(':'))
            day, month = map(int, date_part.split('.'))
            year = datetime.now().year
            return datetime(year, month, day, hours, minutes)
            
    except Exception:
        return None
    return None