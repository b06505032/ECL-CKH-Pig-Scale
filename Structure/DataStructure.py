import queue
from Structure.SerialThread import *

class Pig():
    def __init__(self):
        self.weight = 0.0  # store the weight of the pig after calculating
        self.weight_list = []  # store the measure weights
        self.real_weight_list = []  # store the real weights
        self.std_weight_list = []  # store the weights after filter out the outliers 
        self.std_err = 0.0  # store the standard error of the weight_list
        self.time_list = []  # store the corresponging time
        self.kptest = []  # record the return value of the function kpss_test()
        self.index = 0  # indexing which part of the weight_list passing into the function kpss_test()


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


