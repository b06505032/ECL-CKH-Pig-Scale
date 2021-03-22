from datetime import datetime


class Pig():
    def __init__(self):
        self.weight_list = []
        self.real_weight_list = []
        self.std_weight_list = []
        self.weight = 0.0
        self.std_err = 0.0
        self.mvmean_weight_list = []
        self.time_list = []
        self.kptest = []
        self.index = 0


class Fence():
    def __init__(self):
        self.piglet_num = 0
        self.weight = 0
        self.pig_id = []
        self.piglet_list = []
        p = Pig()
        self.piglet_list.append(p)


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