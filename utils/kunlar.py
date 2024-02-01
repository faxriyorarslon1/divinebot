import datetime


def month_day(month):
    year = datetime.datetime.now().year
    day = []
    month = int(month)
    if int(month) == 1 or int(month) == 3 or int(month) == 5 or int(month) == 7 or int(month) == 8 or int(
            month) == 10 or int(month) == 12:
        for i in range(1, 32):
            day.append(i)
    elif int(month) == 4 or int(month) == 6 or int(month) == 9 or int(month) == 11:
        for i in range(1, 31):
            day.append(i)
    elif (year % 4 == 0) and int(month) == 2:
        for i in range(1, 30):
            day.append(i)
    else:
        for i in range(1, 29):
            day.append(i)
    return day
