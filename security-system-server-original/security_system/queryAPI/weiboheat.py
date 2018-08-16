from datetime import *


def WeekBeforeDate(date):
    week = []
    i = 0
    formatdate = datetime.strptime(date, '%Y%m%d')
    while i < 7:
        day_before_format = formatdate - timedelta(days=i)
        day_before_str = day_before_format.strftime('%Y%m%d')
        week.append(day_before_str)
        i = i + 1
    return week


def DateOfNweeksBefore(date, n):
    formatdate = datetime.strptime(date, '%Y%m%d')
    date_weeks_before_format = formatdate - timedelta(days=n * 7)
    date_weeks_before_str = date_weeks_before_format.strftime('%Y%m%d')
    return date_weeks_before_str
