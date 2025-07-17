import re
from datetime import datetime, timedelta

def parse_cost(coststr):
    return float(coststr.replace('£', '').strip())

def parse_duration(durstr):
    durstr = durstr.strip().lower()
    match = re.match(r'(?:(\d+)h)?(?:(\d+)m)?$', durstr)
    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2)) if match.group(2) else 0
        total_minutes = hours * 60 + minutes
        if total_minutes > 0:
            return total_minutes
    raise ValueError(f'Invalid duration: {durstr}')

def parse_time(timestr):
    """Parse time in HH:MM format, returns minutes since midnight"""
    timestr = timestr.strip()
    match = re.match(r'^(\d{2}):(\d{2})$', timestr)
    if match:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        return hours * 60 + minutes  # minutes since midnight
    raise ValueError(f'Invalid time: {timestr}')

def parse_datetime(datetimestr):
    """Parse datetime in YYYY-MM-DD HH:MM format, returns datetime object"""
    datetimestr = datetimestr.strip()
    try:
        return datetime.strptime(datetimestr, '%Y-%m-%d %H:%M')
    except ValueError:
        # Fallback to time-only parsing for backward compatibility
        return parse_time(datetimestr)

def parse_flexible_schedule(schedulestr):
    """Parse flexible schedule like '05:00-11:00/15m'"""
    schedulestr = schedulestr.strip()
    match = re.match(r'^(\d{2}):(\d{2})-(\d{2}):(\d{2})/(\d+)m$', schedulestr)
    if match:
        start_hour = int(match.group(1))
        start_min = int(match.group(2))
        end_hour = int(match.group(3))
        end_min = int(match.group(4))
        frequency = int(match.group(5))
        
        start_time = start_hour * 60 + start_min
        end_time = end_hour * 60 + end_min
        
        return {
            'start_time': start_time,
            'end_time': end_time,
            'frequency': frequency
        }
    raise ValueError(f'Invalid flexible schedule: {schedulestr}')

def datetime_to_minutes_since_midnight(dt):
    """Convert datetime to minutes since midnight of that day"""
    return dt.hour * 60 + dt.minute

def minutes_since_midnight_to_datetime(minutes, base_date=None):
    """Convert minutes since midnight to datetime object"""
    if base_date is None:
        base_date = datetime.now().date()
    
    hours = minutes // 60
    mins = minutes % 60
    return datetime.combine(base_date, datetime.min.time().replace(hour=hours, minute=mins))