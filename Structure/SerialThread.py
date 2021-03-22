from time import sleep
import threading
from serial import SerialException, Serial
from datetime import datetime
import pytz
from Utils.Logger import print


class SerialThread(threading.Thread):
    def __init__(self, _buadrates, _dataqueue, _timequeue):
        threading.Thread.__init__(self)
        self.dataQueue = _dataqueue
        self.timeQueue = _timequeue
        self.BAUD_RATES = _buadrates
    
    
    def open_port(self, _comport):
        self.ser = Serial(_comport, self.BAUD_RATES, timeout=1)


    def write_data(self, info):
        if self.ser.is_open == True:
            print("serial writing data:"+str(info))
            self.ser.write(info.encode("utf-8"))
        else:
            print("serial write error")

    def start(self):
        threading.Thread.__init__(self)
        threading.Thread.start(self)


    def run(self):
        sleep(0.2)
        while True:
            if self.ser.in_waiting:
                try:
                    text = self.ser.readline()
                    local_dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei'))
                    currentTime = pytz.timezone('Asia/Taipei').normalize(local_dt).strftime('%H:%M:%S\'%f')[:-3]
                    self.timeQueue.put(currentTime)
                    self.dataQueue.put(text)
                except SerialException as e: 
                    print("Serial exception: " + str(e))
                    pass