from datetime import datetime, timedelta


def get_current_time_to_nearest_30_minutes():
    """Return the current time, rounded to the nearest 30 minutes"""
    now = datetime.now()
    minutes = 30 * round(now.minute / 30)
    return now.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minutes)
