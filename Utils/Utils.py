from datetime import datetime

def time():
    now = datetime.now()
    now_time = str(now.hour) + "-" + str(now.minute) + "-" + str(now.second)
    return now_time


def today():
    now = datetime.now()
    if len(str(now.month)) == 1:
        month = "0" + str(now.month)
    else:
        month = str(now.month)    
    if len(str(now.day)) == 1:
        day = "0" + str(now.day)
    else:
        day = str(now.day)
    today = month + day
    return today


def list_to_str(org_list):
    full_str = ', '.join([str(elem) for elem in org_list])
    return full_str