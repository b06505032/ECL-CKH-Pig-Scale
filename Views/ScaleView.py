from tkinter import ttk
import tkinter as tk
from tkinter import *
from os import getcwd
from Utils.Logger import print, list_to_str
from Utils.Utils import today, time
from Structure.DataStructure import Pig, Fence
from datetime import datetime
import pytz
import queue
import pandas as pd
import numpy as np
from Utils.analyze import kpss_test
import inspect
import csv
import ctypes


class ScaleView(tk.Frame):
    def __init__(self, parent, controller, system):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.system = system
        # initial frame
        self.data_frame()
        self.weight_frame()
        self.table_frame()
        # start weighting
        self.system.datafile = open(today()+'_'+time()+'.log',"w")
        f = Fence()
        self.system.fence_list.append(f)
        self.totalWeight = 0.0
        self.zeroing()
        self.system.serialthread.start()
        self.read_data()


    # function for getting the data from queue of the serial and calculate the pig's weight
    def read_data(self):  #讀取資料
        value = True
        while self.system.dataQueue.qsize():
            try:  # get data from queue
                data = self.system.dataQueue.get()
                currentTime = self.system.timeQueue.get()
                # print("original data: "+ str(data))
                data = data.decode().strip("ST,GS,").strip("US,GS,").strip("ST,NT,").strip("ST,TR,").strip("OL,GS")
                data = data.strip().strip("kg").strip().strip("+").replace(" ", "")
                if value:
                    try:  # transfer to float
                        data = float(data)
                        value = False
                        error = 0
                    except:
                        error = 1
                        print("read_data except_error")
                    if not error:
                        self.weight_var.set(data)
                        # local_dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei'))
                        # currentTime = pytz.timezone('Asia/Taipei').normalize(local_dt).strftime('%H:%M:%S\'%f')[:-3]
                        print("serial: " + currentTime + " " + str(data))
                        self.system.datafile.write(currentTime + " " + str(data) + "\n")
                        
                        ##########  Algorithms Part  ##########
                        if (data - self.totalWeight) >= self.system.threshold:  #  record weight
                            self.system.fence_list[-1].piglet_list[-1].weight_list.append(data)
                            self.system.fence_list[-1].piglet_list[-1].time_list.append(currentTime)
                            self.pig_weight_show.configure(bg="gray77",fg="gray77")
                            self.litter_weighing_show.configure(bg="gray77",fg="gray77")
                        elif (self.totalWeight - data) >= self.system.threshold:  #  pick up pig
                            if data < self.system.threshold and data >=0:
                                self.litter_weight.set(str(round(self.system.fence_list[-1].weight,2))+"kg")
                                self.litter_weighing_show.configure(bg="white",fg="black")
                                self.en_sow.configure(font=("Calibri",26),width=10, fg="red")
                                self.input_sow_id.set("請輸入耳號")
                                self.totalWeight = 0.0
                                self.clear_table()
                                self.system.datafile.close()
                                self.system.datafile = open(today()+'_'+time()+'.log',"w")
                                f = Fence()
                                self.system.fence_list.append(f)
                                self.zeroing()
                        # claculate the average
                        statement = False  #自動/手動決定重量有不同的判斷式
                        if (len(self.system.fence_list[-1].piglet_list[-1].weight_list)) >= self.system.sampleSize:
                            if self.system.autoMode:
                                statement = True
                        if str(self.focus_get()) == ".!frame.!frame.!button2":
                            if not self.system.autoMode:
                                statement = True
                                local_dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei'))
                                tmp = pytz.timezone('Asia/Taipei').normalize(local_dt).strftime('%H:%M:%S\'%f')[:-3] +  " press_decide_weight_button\n"
                                self.system.datafile.write(tmp) #記錄按按鈕的時間
                        if statement:
                            # check if stationary or not
                            index = self.system.fence_list[-1].piglet_list[-1].index
                            temp_list = self.system.fence_list[-1].piglet_list[-1].weight_list[index:index+self.system.sampleSize]
                            time_list = self.system.fence_list[-1].piglet_list[-1].time_list[index:index+self.system.sampleSize]
                            self.system.fence_list[-1].piglet_list[-1].index += 1
                            # pass the temp_list and time_list into kpss_test function to check if it is stationary or not
                            ser_data = pd.Series(temp_list, index=time_list)
                            self.system.fence_list[-1].piglet_list[-1].kptest.append(1 if kpss_test(ser_data) else 0)  # record the kpss return value
                            if len(self.system.fence_list[-1].piglet_list[-1].kptest) < 5:
                                continue  # less than five times
                            if self.system.fence_list[-1].piglet_list[-1].kptest[-5:] != [1]*5:
                                continue  # the latest five value is not stationary
                            # is stationary! -> calculate the average
                            temp_list = self.system.fence_list[-1].piglet_list[-1].weight_list[index-4:index+self.system.sampleSize]
                            temp_list = [round(i-self.totalWeight, 2) for i in temp_list]  # minus the former totalWeight to get actual weight
                            last_ave = round(np.mean(temp_list), 2)  # get the average
                            self.system.fence_list[-1].piglet_list[-1].weight = last_ave  # record the pig weight actual value
                            self.totalWeight += last_ave  # renew totalWeight
                            self.system.fence_list[-1].weight = self.totalWeight  # record the fence weight


                            # 儲存豬耳號
                            temp_ID=[self.input_sow_id.get() ,self.input_piglet_id.get()]
                            self.system.fence_list[-1].pig_id.append(temp_ID)  # record ID
                            self.tree.insert("","end",values=[self.input_piglet_id.get(), str(last_ave)])  # add pigID and weight in the table
                            self.update_minmax(last_ave)  # update the min and max value
                            # claculate pig number
                            if self.system.fence_list[-1].piglet_list is not []:
                                self.piglet_save_num.set("已存豬數："+str(len(self.system.fence_list[-1].piglet_list)))
                                self.system.fence_list[-1].piglet_num = len(self.system.fence_list[-1].piglet_list)
                            # show information on GUI
                            self.piglet_weight.set(str(round(self.system.fence_list[-1].piglet_list[-1].weight,2))+"kg")
                            self.pig_weight_show.configure(bg="white",fg="black")
                            self.en_piglet.configure(font=("Calibri",26),width=10, fg="red")
                            self.input_piglet_id.set("請輸入耳號")
                            # create a new pig, be ready to weight the next pig
                            p = Pig()
                            self.system.fence_list[-1].piglet_list.append(p)   
            except queue.Empty:
                pass
        self.weight_value_show = self.label_weighing_nowshow.after(100, self.read_data)


    # function for removing the value in the GUI table
    def clear_table(self):
        self.tree.delete(*self.tree.get_children())
        self.min_max.delete(*self.min_max.get_children())
        self.min_var.set(10000)
        self.max_var.set(0.0)
        self.min_max.insert("","end",values=[self.min_var.get(), self.max_var.get()])


    # command for pressing stop weighting button
    def stop_weighting(self):
        self.label_weighing_nowshow.after_cancel(self.weight_value_show)
        self.system.serialthread.ser.reset_input_buffer()
        self._async_raise(self.system.serialthread.ident, SystemExit)
        self.system.serialthread.join()  
        print("Stopped!")
        self.system.datafile.close()
        self.system.serialthread.ser.close()
        print("===STOP WEIGHTING DEBUG PART===")
        print(len(self.system.fence_list))
        for i in range(self.system.fence_list[0].piglet_num):
            print("length: " +str(len(self.system.fence_list[0].piglet_list[i].weight_list)))
            print(self.system.fence_list[0].piglet_list[i].weight)
        print("===STOP WEIGHTING DEBUG PART===")
        self.output_csv()


    # function for updating the min and max value in the GUI table
    def update_minmax(self, value):
        if value < self.min_var.get():
            self.min_max.delete(*self.min_max.get_children())
            self.min_var.set(value)
            self.min_max.insert("","end",values=[self.min_var.get(), self.max_var.get()])
        if value > self.max_var.get():
            self.min_max.delete(*self.min_max.get_children())
            self.max_var.set(value)
            self.min_max.insert("","end",values=[self.min_var.get(), self.max_var.get()])

    
    # function for stopping the thread when user presses stopping weighting button
    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")


    # function for outputing the csv file when user presses stoping weighting button
    def output_csv(self):
        file_path = getcwd() #取路徑的資料
        with open(file_path + "/" + today() + "weaned weight" +'.csv','a+',encoding="utf-8",newline='') as csv_file:
            write = csv.writer(csv_file)
            header = ["sow id", "piglet id", "weight","fence weight","number born alive"]
            write.writerow(header)
            print("===OUTPUT CSV DEBUG PART===")
            for j in range(len(self.system.fence_list)-1):
                print("fence_weight: "+str(self.system.fence_list[j].weight)) # 印在終端機的
                if self.system.fence_list[j].weight is not None:       
                    for i in range(len(self.system.fence_list[j].piglet_list)-1):        
                        print("pig_weight: "+str(self.system.fence_list[j].piglet_list[i].weight)) 
                        temp = self.system.fence_list[j].pig_id[i] # [母豬，小豬]
                        temp.append(str(self.system.fence_list[j].piglet_list[i].weight)) # [母豬，小豬，小豬重量]
                        print(list_to_str(temp)) # 印在終端機的
                        write.writerow(temp)
                temp1 = ["", "", "", self.system.fence_list[j].weight, len(self.system.fence_list[j].piglet_list)-1]
                write.writerow(temp1)
            print("===OUTPUT CSV DEBUG PART===")


    # command for pressing the decide weight button
    def decide_weight(self):
        self.btn_decide_weight.focus_set()


    # command for zeroing the scale
    def zeroing(self):
        self.system.serialthread.write_data("MZ\r\n")
        self.weight_var.set(0.0)

    
    # show the weight in GUI
    def weight_frame(self):
        weightFrame = tk.Frame(self, bd=1, padx=10, pady=10, relief=RAISED)
        
        self.weight_var = tk.StringVar()
        self.weight_var.set("0.0kg")   
        lb_current_weight = tk.Label(weightFrame, text="目前秤值", font=20)
        lb_current_weight.pack(side=TOP, anchor=tk.W)
        self.label_weighing_nowshow = tk.Label(weightFrame, textvariable=self.weight_var, 
                    font=("Calibri", 90), bd=2, anchor=tk.E, width=7, height=1, bg="white", fg="black", padx=10)
        self.label_weighing_nowshow.pack(side=TOP, pady=5, fill=X)
        
        sub_frm = tk.Frame(weightFrame, padx=10, pady=4)
        btn_zero = tk.Button(sub_frm,text="歸零", command = self.zeroing, font=20)
        btn_zero.pack(side=RIGHT, pady=4, anchor=tk.E)
        if not self.system.autoMode:
            self.btn_decide_weight = tk.Button(sub_frm,text="決定重量", font=10, command=self.decide_weight)
            self.btn_decide_weight.pack(side=RIGHT, padx=5, pady=4, anchor=tk.E)
        sub_frm.pack(side=TOP, fill=X)
        
        self.piglet_save_num, self.litter_weight, self.piglet_weight = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.piglet_save_num.set("已存豬數：0")
        self.litter_weight.set("0.0kg")
        self.piglet_weight.set("0.0kg")

        lb_pig_weight = tk.Label(weightFrame,text="仔豬重",font=20)
        lb_pig_weight.pack(side=TOP,anchor=tk.W)
        self.pig_weight_show = tk.Label(weightFrame, textvariable=self.piglet_weight,font=("Calibri",60),bd=1,anchor=tk.W,bg="gray77",fg="gray77",padx=10,width=11,height=1)
        self.pig_weight_show.pack(side=TOP,pady=5)
        
        lb_litter_weighing = tk.Label(weightFrame, text="窩重",font=20)
        lb_litter_weighing.pack(side=TOP, anchor=tk.W)
        self.litter_weighing_show = tk.Label(weightFrame, textvariable=self.litter_weight,font=("Calibri",60),bd=1,anchor=tk.W,bg="gray77",fg="gray77",padx=10,width=11,height=1)
        self.litter_weighing_show.pack(side=TOP, pady=5)

        button = tk.Button(weightFrame, text="結束並儲存",
                           command=lambda: [self.stop_weighting(), self.controller.show_frame("StartView", self.system)])
        button.pack(side=TOP)

        weightFrame.pack(side=LEFT)


    # function for changing color when the user click on the inout of data frame
    def change_color(self, event): #點擊widget時，改變其顏色 
        widget = self.dataFrame.focus_get()
        if self.en_sow['fg']=="red" and str(widget) == ".!labelframe2.!entry":
            self.input_sow_id.set("")
            self.en_sow.configure(font=("Calibri",33),width=8, fg="black")
        elif self.en_piglet['fg']=="red" and str(widget) == ".!labelframe2.!entry2":
            self.input_piglet_id.set("")
            self.en_piglet.configure(font=("Calibri",33),width=8, fg="black")


    # a frame that allows the user to input sowID and pigletID
    def data_frame(self):
        self.dataFrame = ttk.LabelFrame(self, text="耳號設定", relief=RIDGE)
        
        self.input_sow_id, self.input_piglet_id = tk.StringVar(), tk.StringVar()
        self.input_sow_id.set("請輸入耳號")
        self.input_piglet_id.set("請輸入耳號")
        lb_sow =  tk.Label(self.dataFrame, text="母豬耳號", font=13)
        lb_sow.pack(side=TOP, padx=10, pady=5, anchor=tk.W)
        self.en_sow = tk.Entry(self.dataFrame, textvariable = self.input_sow_id, font=("Calibri",26),width=10, fg="red")
        self.en_sow.pack(side=TOP, padx=10, pady=5,ipady=3)
        self.bind("<Button-1>", lambda e: self.change_color(e))
        lb_piglet = tk.Label(self.dataFrame, text="仔豬耳號", font=13)
        lb_piglet.pack(side=TOP, padx=10, pady=5, anchor=tk.W)
        self.en_piglet = tk.Entry(self.dataFrame, textvariable = self.input_piglet_id, font=("Calibri",26),width=10, fg="red")
        self.en_piglet.pack(side=TOP, padx=10, pady=5,ipady=3)
        
        self.dataFrame.pack(side=LEFT)


    # a frame that shows the table on GUI
    def table_frame(self):
        tableFrame = tk.Frame(self, bd=1, padx=10, pady=10, relief=RIDGE)
        
        self.tree=ttk.Treeview(tableFrame, columns=["1","2"],show="headings",height=25)
        vsb = ttk.Scrollbar(tableFrame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.column("1",width=100,anchor="center")
        self.tree.column("2",width=100,anchor="center")
        self.tree.heading("1",text="小豬")
        self.tree.heading("2",text="重量")
        self.min_var, self.max_var = tk.DoubleVar(), tk.DoubleVar()
        self.min_var.set(10000)
        self.max_var.set(0.0)

        self.min_max = ttk.Treeview(tableFrame,columns=["1","2"],show="headings",height=1)
        self.min_max.column("1",width=100,anchor="center")
        self.min_max.column("2",width=100,anchor="center")
        self.min_max.heading("1",text="最小值")
        self.min_max.heading("2",text="最大值")
        self.min_max.pack()
        '''
        for i in range(30):
            data = i+1.0
            self.tree.insert("","end",values=["1000-"+str(i),data])
            if min_var.get() > data:
                min_var.set(data)
                print("min:"+str(min_var.get()))  
            if max_var.get() < data:
                max_var.set(data)
                print("max:"+str(max_var.get()))
        '''
        self.min_max.insert("","end",values=[self.min_var.get(), self.max_var.get()])
        
        tableFrame.pack(side=RIGHT)
