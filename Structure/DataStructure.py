import queue
from Structure.SerialThread import *

class Pig():
    def __init__(self):
        self.weight_list = []
        self.real_weight_list = []
        self.std_weight_list = []
        self.weight = 0.0
        self.std_err = 0.0
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


class Scale():
    def __init__(self):
        self.threshold = 3.0
        self.sampleSize = 40
        self.port = ""
        self.autoMode = True
        self.dataQueue = queue.Queue()
        self.timeQueue = queue.Queue()
        self.serialthread = SerialThread(9600, self.dataQueue, self.timeQueue)
        self.fence_list = []


