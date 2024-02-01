from datetime import datetime
import pytz


def date_time_check():
    date = pytz.timezone('Asia/Tashkent').localize(datetime.now())
    start_time = "0"
    end_time = "0"
    if 12 > date.hour >= 8:
        start_time = "8"
        end_time = "12"
    if 17 > date.hour >= 12:
        start_time = "12"
        end_time = "17"
    if 20 > date.hour >= 17:
        start_time = "17"
        end_time = "20"
    start = str(date)[0:11]
    end = str(date)[19:]
    if start_time != "0":
        start_finish = start + start_time + ':00:00' + end
        end_finish = start + end_time + ':00:00' + end
    else:
        start_finish = None
        end_finish = None
    return start_finish, end_finish


def admin_send_location_user():
    date = pytz.timezone('Asia/Tashkent').localize(datetime.now())

    start_time = "8"
    end_time = "9"
    start_minute = '30'
    start = str(date)[0:11]
    end1 = str(date)[26:]
    end2 = str(date)[26:]
    start_minute = str(start_minute)
    start_finish = start + start_time + ":" + "00" + ":" + "00" + "." + "000000" + end1
    end_finish = start + end_time + ":" + start_minute + ":" + "00" + "." + '000000' + end2
    return start_finish, end_finish


print(admin_send_location_user())
