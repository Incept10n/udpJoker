from datetime import datetime, timedelta
import os
import json
import re

# Загрузка данных
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_notifications(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_notifications(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_time(time_str):
    time_str = time_str.strip().lower()
    now = datetime.now()
    
    # Формат "15:30"
    if re.match(r'^\d{1,2}:\d{2}$', time_str):
        hours, minutes = map(int, time_str.split(':'))
        target_time = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
        if target_time < now:
            target_time += timedelta(days=1)  # Если время уже прошло, ставим на завтра
        return target_time.strftime("%H:%M")
    
    # Формат "14:25 25.12"
    elif re.match(r'^\d{1,2}:\d{2} \d{1,2}\.\d{1,2}$', time_str):
        time_part, date_part = time_str.split(' ')
        hours, minutes = map(int, time_part.split(':'))
        day, month = map(int, date_part.split('.'))
        year = now.year
        target_time = datetime(year, month, day, hours, minutes)
        return target_time.strftime("%H:%M %d.%m")
    
    # Формат "через X часов"
    elif "час" in time_str:
        match = re.search(r'(\d+)\s*час', time_str)
        if match:
            hours = int(match.group(1))
            target_time = now + timedelta(hours=hours)
            return target_time.strftime("%H:%M")
    
    # Формат "через X минут"
    elif "минут" in time_str:
        match = re.search(r'(\d+)\s*минут', time_str)
        if match:
            minutes = int(match.group(1))
            target_time = now + timedelta(minutes=minutes)
            return target_time.strftime("%H:%M")
    
    return None












