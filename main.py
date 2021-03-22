#!/usr/bin/env python
# coding: utf-8



import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk
from tkinter import simpledialog as sd
from tkinter import filedialog as fd
from tkinter import *
from datetime import datetime
import serial
import serial.tools.list_ports
from statistics import mean
import csv
import xlrd
import logging
from prettytable import PrettyTable
import numpy as np
import os


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


# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    # format='%(asctime)s %(name)-4s %(message)s',
                    format='%(asctime)s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='terminal'+today()+'_'+time()+'.log',
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)
# Now, we can log to the root logger, or any other logger. First the root...
logging.info('Start logging...')
# Now, define a couple of other loggers which might represent areas in your
# application:
logger = logging.getLogger('info')


def print(_str):
    logger.debug(_str)

def list_to_str(org_list):
    full_str = ', '.join([str(elem) for elem in org_list])
    return full_str




class PigGUI(tk.Tk):
    
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("仔豬磅秤")
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        self.geometry("900x500+200+200")
        self.setting_frame()
        self.weight_frame()
        self.data_frame()
        self.record_frame()
        self.myserial = mySerialPort(9600)
        self.record_list = []
        self.save_setting()
        self.select_folder()
        # self.total_weight_setting()
        # self.earmark_setting()
        # self.piglet_setting()
        
        self.data_list = [0.0]
        self.fence_list = []
        self.last_ave = 0.0
        self.pig_id_list = []
        self.record_history("完成初始化")


    def select_folder(self):
         temp = self.storage_path_var.get()
         user_input = fd.askdirectory(title = "秤重資料儲存資料夾")
         if user_input is not str():
             self.storage_path_var.set(user_input)
             self.record_history("資料儲存路徑更動:"+user_input)
            
         else:
             self.storage_path_var.set(temp)
    
    
    def select_file(self):
        filename =  fd.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
        if filename is not None:
            print(str(type(filename)))
            with open(filename, newline='') as csvfile:
                rows = csv.reader(csvfile, delimiter=',')
                for row in rows:
                    # print(type(row))
                    print(str(row[0]) +" "+str(row[1]))
        self.record_history("成功上傳豬隻耳號資料")
         

    def record_history(self, _record_str):
        self.record_list.append(_record_str)
        self.text_history.configure(state='normal')
        self.text_history.insert(tk.END, _record_str+"\n")
        self.text_history.yview_pickplace("end")
        self.text_history.configure(state='disabled')


    def setting_frame(self):
        frm_1 = tk.Frame(self)
        frm_1.place(x=10,y=10)
        self.btn_set1 = tk.Button(frm_1,text="設定儲存鎖定值", command=self.save_setting)
        self.btn_set1.grid(row=0,column=0)
        self.btn_set2 = tk.Button(frm_1,text="秤重資料儲存",command=self.output_csv)
        self.btn_set2.grid(row=0,column=1)
        self.btn_set3 = tk.Button(frm_1,text="上傳豬隻身分資料",command=self.select_file)
        self.btn_set3.grid(row=1,column=0)
        self.btn_set4 = tk.Button(frm_1,text="設定資料儲存路徑",command=self.select_folder)
        self.btn_set4.grid(row=1,column=1)
        self.btn_connect = tk.Button(frm_1,command=self.connecting,text="連線")
        self.btn_connect.grid(row=0,column=2)
        self.btn_weighing = tk.Button(frm_1,command=self.weighing,text="開始秤重", state = DISABLED)
        self.btn_weighing.grid(row=1,column=2)
        
        port_list = list(serial.tools.list_ports.comports())
        assert (len(port_list) != 0),"无可用串口"
        port_str_list = []
        for i in range(len(port_list)):
            # 将串口号切割出来
            lines = str(port_list[i])
            print("port: " + str(i) + " " + str(port_list[i]))
            str_list = lines.split(" ")
            port_str_list.append(str_list[0])
        self.port_var = tk.StringVar()
        cbb_com = ttk.Combobox(frm_1,values=port_str_list, textvariable = self.port_var, state="readonly", width=12)
        cbb_com.grid(row=2,column=0)
        
        cbb_staff = ttk.Combobox(frm_1,values=["小明","阿嬌"], width=12)
        cbb_staff.grid(row=2,column=1)

        self.ac_rate = tk.IntVar()  # 選擇速率
        cbb_rate = ttk.Combobox(frm_1,values=[1, 2, 4, 8, 16], textvariable = self.ac_rate, state="readonly", width=12)
        self.ac_rate.set(1)
        cbb_rate.grid(row=2,column=2)
    
    def data_frame(self):
        frm_2 = tk.Frame(self)
        frm_2.place(x=10,y=200)
        
        frm_2_up = tk.Frame(frm_2)
        frm_2_down = tk.Frame(frm_2)
        frm_2_up.pack(side='top')
        frm_2_down.pack(side='bottom')

        self.sow_id, self.pig_id = tk.StringVar(), tk.StringVar()
        self.sow_id.set("default")
        self.pig_id.set("default")

        lb_sow =  tk.Label(frm_2_up,text="母豬資料")
        lb_sow.grid(row=0,column=0)
        lb_smallpig = tk.Label(frm_2_up,text="仔豬資料")
        lb_smallpig.grid(row=0,column=1)
        en_sow = tk.Entry(frm_2_up, textvariable = self.sow_id)
        en_sow.grid(row=1,column=0)
        en_smallpig = tk.Entry(frm_2_up, textvariable = self.pig_id)
        en_smallpig.grid(row=1,column=1)
        
        btn_zero = tk.Button(frm_2_down,text="歸零", command = self.zeroing)
        btn_zero.grid(row=0,column=0)
        btn_clean = tk.Button(frm_2_down,text="清除上筆")
        btn_clean.grid(row=0,column=1)
        
        btn_get_record_data = tk.Button(frm_2_down,text="取得歷史測試資料", command=self.get_record_file)
        btn_get_record_data.grid(row=1,column=0)
        btn_analyze_data1 = tk.Button(frm_2_down,text="分析測試資料1", command=self.analyze_data1)
        btn_analyze_data1.grid(row=2,column=0)
        Hovertip(btn_analyze_data1, "直接取平均", hover_delay=100)
        btn_analyze_data2 = tk.Button(frm_2_down,text="分析測試資料2", command=self.analyze_data2)
        btn_analyze_data2.grid(row=2,column=1)
        Hovertip(btn_analyze_data2, "前兩筆不計，取平均", hover_delay=100)
        btn_analyze_data3 = tk.Button(frm_2_down,text="分析測試資料3", command=self.analyze_data3)
        btn_analyze_data3.grid(row=2,column=2)
        Hovertip(btn_analyze_data3, "算標準差，刪除異端值，取平均", hover_delay=100)
       
        
    def weight_frame(self):
        frm_3 = tk.Frame(self)
        frm_3.place(x=450,y=10)
        lb_nowshow = tk.Label(frm_3,text="目前秤值")
        lb_nowshow.grid(row=0,column=0)
        self.weight_var = tk.StringVar()
        self.weight_var.set(0)
        ####
        # label_weighing_nowshow = tk.Label(frm_3,height=5,textvariable=self.weight_var,width=20)
        # label_weighing_nowshow.grid(row=1,column=0)
        
        self.label_weighing_nowshow = tk.Label(frm_3,height=5,textvariable=self.weight_var,width=20)
        self.label_weighing_nowshow.grid(row=1,column=0)
        
        self.piglet_save_num, self.last_piglet_weight, self.pig_weight = tk.IntVar(), tk.DoubleVar(), tk.StringVar()
        self.piglet_save_num.set(0)
        self.last_piglet_weight.set(0.0)
        self.pig_weight.set("")

        lb_lastshow = tk.Label(frm_3,text="上頭豬重量")
        lb_lastshow.grid(row=2,column=1)
        lb_savenum = tk.Label(frm_3,text="已存豬數")
        lb_savenum.grid(row=2,column=0)
        pig_weight_show = tk.Label(frm_3,textvariable=self.pig_weight, font=30)
        pig_weight_show.grid(row=1,column=2)
        text_weighing_lastshow = tk.Label(frm_3,height=1,textvariable=self.last_piglet_weight ,width=20)
        text_weighing_lastshow.grid(row=3,column=1)
        text_weighing_savenum = tk.Label(frm_3,height=1,textvariable=self.piglet_save_num,width=20)
        text_weighing_savenum.grid(row=3,column=0)

    def record_frame(self):
        frm_4 = tk.Frame(self)
        frm_4.place(x=450,y=200)
        
        setting = tk.Label(frm_4,text="設定內容")
        setting.grid(row=0,column=1)
        # history = tk.Label(frm_4,text="歷史紀錄")
        # history.grid(row=0,column=2)
        
        setting_context = tk.LabelFrame(frm_4,padx=5, pady=5)
        setting_context.grid(column=0,row=1)
        r1 = tk.Label(setting_context, text="狀態:").grid(row=0, column=0)
        r2 = tk.Label(setting_context, text="儲存鎖定值:").grid(row=1, column=0)
        r3 = tk.Label(setting_context, text="總重鎖定值:").grid(row=2, column=0)
        r4 = tk.Label(setting_context, text="運算速度:").grid(row=3, column=0)
        r5 = tk.Label(setting_context, text="紀錄路徑:").grid(row=4, column=0)
        r6 = tk.Label(setting_context, text="秤電量:").grid(row=5, column=0)

        setting_entry = tk.LabelFrame(frm_4,padx=20, pady=5)
        setting_entry.grid(row=1, column=1)
        
        self.status_var, self.save_var, self.total_weight_var, self.storage_path_var = tk.StringVar(), tk.DoubleVar(), tk.DoubleVar(), tk.StringVar()
        self.status_var.set("disconnect")
        self.save_var.set(0.0) # 初始值0
        self.total_weight_var.set(0.0)
        self.storage_path_var.set(os.getcwd())
        setting1 = tk.Label(setting_entry,width=10,textvariable=self.status_var).grid(row=0, column=0)
        setting2 = tk.Label(setting_entry,width=10,textvariable=self.save_var).grid(row=1, column=0)
        setting3 = tk.Label(setting_entry,width=10,textvariable=self.total_weight_var).grid(row=2, column=0)
        setting4 = tk.Label(setting_entry,width=10).grid(row=3, column=0)
        setting5 = tk.Label(setting_entry,width=10,textvariable=self.storage_path_var).grid(row=4, column=0)
        setting6 = tk.Label(setting_entry,width=10).grid(row=5, column=0)

        # record history
        # self.text_history = scrolledtext.ScrolledText(frm_4,height=10,width=20)
        # self.text_history.grid(row=1,column=2)
        self.record_window()

    def record_window(self):
        top = Toplevel()
        top.title('Record')
        top.wm_geometry("220x270")
        top.resizable(width=False, height=False)
        optimized_canvas = Canvas(top)
        optimized_canvas.pack(fill=BOTH, expand=1)
        self.text_history = scrolledtext.ScrolledText(optimized_canvas, state='disabled', height=20,width=30)
        optimized_image = optimized_canvas.create_window(0, 0, anchor=NW, window=self.text_history)


    def zeroing(self):
        self.myserial.write_data("MZ\r\n")
        self.weight_var.set(0.0)
        
        
    def connecting(self):
        temp = self.port_var.get()
        try:
            self.myserial.open_port(temp)
            self.status_var.set("connect")
            self.record_history("連線")
            self.btn_connect.configure(text="中斷連線",command=self.disconnect)
            self.btn_weighing.configure(state=NORMAL)
        except:
            tk.messagebox.showwarning(title="錯誤",message='請選擇串口埠')


    def disconnect(self):
        self.myserial.ser.close()
        self.record_history("中斷連線")
        self.status_var.set("disconnect")
        self.btn_connect.configure(text="連線",command=self.connecting)
        self.btn_weighing.configure(state=DISABLED)
    
    def weighing(self):
        # start reading
        if self.myserial.opened:
            self.zeroing()
            self.datafile = open(today()+'_'+time()+self.sow_id.get()+'.log',"w")
            f = Fence() # create a new fence
            self.fence_list.append(f)
            self.label_weighing_nowshow.after(0, self.read_data)
            self.record_history("開始秤重")
            self.btn_weighing.configure(text = "結束並儲存",command=self.stop_weighing)
            self.btn_connect.configure(state = DISABLED)
            self.btn_set1.configure(state = DISABLED)
            self.btn_set2.configure(state = DISABLED)
            self.btn_set3.configure(state = DISABLED)
            self.btn_set4.configure(state = DISABLED)
        else:
            print("serial is not open!!!!!!!!!!!!")
            tk.messagebox.showwarning(title="錯誤",message='尚未連線!!!!!!!!')

    def stop_weighing(self):
        self.label_weighing_nowshow.after_cancel(self.weight_value_show)
        self.record_history("停止秤重")
        self.btn_weighing.configure(text = "開始秤重",command=self.weighing)
        self.btn_connect.configure(state = NORMAL)
        self.btn_set1.configure(state = NORMAL)
        self.btn_set2.configure(state = NORMAL)
        self.btn_set3.configure(state = NORMAL)
        self.btn_set4.configure(state = NORMAL)
        self.datafile.close()
        self.output_csv()
        

    def output_csv(self):
        file_path = self.storage_path_var.get()

        with open(file_path + "/" + today() + "weaned weight" +'.csv','a+') as csv_file:
            write = csv.writer(csv_file)
            header = ["pig id", "weight", "raw data"]
            write.writerow(header)
            for j in range(len(self.fence_list)-1):
                i = len(self.fence_list[j].piglet_list)-1
                k = i*j
                for i in range(len(self.fence_list[j].piglet_list)-1):
                    temp = [self.pig_id_list[k],self.fence_list[j].piglet_list[i].weight]
                    temp.extend(self.fence_list[j].piglet_list[i].weight_list)
                    write.writerow(temp)
                    k = k + 1
                temp1 = ["", "", "total", self.fence_list[j].weight]
                write.writerow(temp1)


    def read_data(self):  #讀取資料
        if self.myserial.ser.is_open == True:
            # get last data
            last_data = self.data_list[-1]
            
            # read current data
            self.myserial.write_data("RW\r\n")
            data_raw = self.myserial.ser.readline()  # 讀取一行
            data = data_raw.decode("utf-8")   # 用預設的UTF-8解碼
            print("original data: "+ str(data_raw))
            
            data = data.strip("ST,GS,").strip("US,GS,").strip("ST,NT,").strip("ST,TR,").strip("OL,GS")
            data = data.strip().strip("kg").replace(" ", "")
            if data == "MZ":
                data = 0.0
            
            try:
                data = float(data)  # transfer string to float
                error = 0
            except:
                error = 1
            
            if not error:
                self.datafile.write(time()+" "+str(data)+"\n")
                self.weight_var.set(data)
                self.data_list.append(data)

                ##########  Algorithms Part  ##########
                # print("total_weight_var: " + str(self.total_weight_var.get()))
                if (data - self.total_weight_var.get()) >= self.save_var.get():  #  record weight
                    self.fence_list[-1].piglet_list[-1].weight_list.append(data)
                elif (last_data - data) >= self.save_var.get():  #  pick up pig
                    if data < self.save_var.get():
                        self.pig_weight.set("窩重:"+str(self.fence_list[-1].weight))
                        self.record_history("窩重:"+str(self.fence_list[-1].weight))
                        self.total_weight_var.set(0)
                        self.datafile.close()
                        self.datafile = open(today()+'_'+time()+self.sow_id.get()+'.log',"w")
                        f = Fence()
                        self.fence_list.append(f)
                        self.zeroing()
                        
                
                # claculate the average
                if(len(self.fence_list[-1].piglet_list[-1].weight_list)) >= 32:
                    temp_list = list(self.fence_list[-1].piglet_list[-1].weight_list)
                    # print("record weight: " + list_to_str(temp_list))
                    for i in range(len(temp_list)):
                        temp_list[i] -= self.total_weight_var.get()
                    # print("calculate weight: "+ list_to_str(temp_list))
                    self.last_ave = round(mean(temp_list),2)
                    self.fence_list[-1].piglet_list[-1].weight = self.last_ave
                    self.total_weight_var.set(self.total_weight_var.get()+self.last_ave)
                    # print("average weight: " + str(self.last_ave))
                    self.fence_list[-1].weight = self.total_weight_var.get()

                    #儲存豬耳號
                    id_list = [self.sow_id.get(),self.pig_id.get()]
                    self.pig_id_list.append(id_list)
                    # print(list_to_str(self.pig_id_list))

                    # claculate pig number
                    if self.fence_list[-1].piglet_list is not []:
                        self.piglet_save_num.set(len(self.fence_list[-1].piglet_list))
                        self.fence_list[-1].piglet_num = len(self.fence_list[-1].piglet_list)

                    self.pig_weight.set("小豬重: "+str(round(self.fence_list[-1].piglet_list[-1].weight,2)))
                    self.record_history("儲存成功!")
                    self.record_history("重量："+str(self.fence_list[-1].piglet_list[-1].weight))

                    #顯示上頭豬的重量
                    self.last_piglet_weight.set(round(self.last_ave, 2))
                    
                    p = Pig()  # create a new pig
                    self.fence_list[-1].piglet_list.append(p)
                    #self.pig_weight.set("")
                    

                ##########  Degugging Part  ##########
                print("Total Fence num: {}".format(len(self.fence_list)))
                for j in range(len(self.fence_list)):
                    print("No. " + str(j+1)+ "fence. " + "has " + str(len(self.fence_list[j].piglet_list)) + " pig(s).")
                    for i in range(len(self.fence_list[j].piglet_list)):
                        print("No. "+ str(i+1)+ " pig weight: " + list_to_str(self.fence_list[j].piglet_list[i].weight_list))
                ##########  Debugging Part  ##########

            t = 1000
            if self.ac_rate.get() == 1:
                t = 1000
            elif self.ac_rate.get() == 2:
                t = 500
            elif self.ac_rate.get() == 4:
                t = 250
            elif self.ac_rate.get() == 8:
                t = 125
            elif self.ac_rate.get() == 16:
                t = 62
            self.weight_value_show = self.label_weighing_nowshow.after(250, self.read_data)
            
        else:
            print("serial is not open")
            tk.messagebox.showwarning(title="錯誤",message='尚未連線')
       
    
    def get_record_file(self):
        filename =  fd.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("log files","*.log"),("all files","*.*")))
        if filename is not None:
            with open(filename, 'r') as file_to_read:
                self.weight_values = []
                while True:
                    lines = file_to_read.readline()
                    if not lines:
                        break
                    item = [i for i in lines.split()]
                    self.weight_values.append(item[1])

        
    def analyze_data1(self):
        # 取10筆data
        _datalist = [0.0]
        self.fence_list = []
        f = Fence()
        self.fence_list.append(f)
        total_weight = 0.0
        for i in range(len(self.weight_values)):
            last_data = _datalist[-1]
            try:
                data = float(self.weight_values[i])
            except:
                continue
            _datalist.append(data)
            
            ##########  Algorithms Part  ##########
            if (data - total_weight) >= self.save_var.get():  #  record weight
                self.fence_list[-1].piglet_list[-1].weight_list.append(data)
            elif (last_data - data) >= self.save_var.get():  #  pick up pig
                if data < self.save_var.get():
                    total_weight = 0.0
                    f = Fence()
                    self.fence_list.append(f)
            
            # claculate the average
            if(len(self.fence_list[-1].piglet_list[-1].weight_list)) >= 10:
                temp_list = list(self.fence_list[-1].piglet_list[-1].weight_list)
                for i in range(len(temp_list)):
                    temp_list[i] -= total_weight
                    temp_list[i] = round(temp_list[i],2)
                self.fence_list[-1].piglet_list[-1].real_weight_list = temp_list
                self.last_ave = round(mean(temp_list),2)
                self.fence_list[-1].piglet_list[-1].weight = self.last_ave
                total_weight += self.last_ave
                self.fence_list[-1].weight = total_weight

                #儲存豬耳號
                # id_list = [self.sow_id.get(),self.pig_id.get()]
                # self.pig_id_list.append(id_list)
                # print(li_to_str(self.pig_id_list))

                p = Pig()  # create a new pig
                self.fence_list[-1].piglet_list.append(p)
                self.fence_list[-1].piglet_num = len(self.fence_list[-1].piglet_list) -1
            
        print("analyze method 1  取10筆data, 直接算平均")
        x = PrettyTable()
        x.field_names = ["pig","1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "weight"]
        for j in range(len(self.fence_list)):
            temp = ["No.",j+1,"Fence","","","","","","","","",""]
            x.add_row(temp)
            for i in range(len(self.fence_list[j].piglet_list)):
                temp = [str(i+1)+"_1"]
                temp.extend(list(self.fence_list[j].piglet_list[i].weight_list))
                temp.append(self.fence_list[j].piglet_list[i].weight)
                while(len(temp) < 12):
                    temp.append("none")
                x.add_row(temp)
                temp = [str(i+1)+"_2"]
                temp.extend(list(self.fence_list[j].piglet_list[i].real_weight_list))
                temp.append(self.fence_list[j].piglet_list[i].weight)
                while(len(temp) < 12):
                    temp.append("none")
                x.add_row(temp)
        print(x)
        
    
    def analyze_data2(self):
        # 取10筆data , 前2個不計
        _datalist = [0.0]
        self.fence_list = []
        f = Fence()
        self.fence_list.append(f)
        total_weight = 0.0
        for i in range(len(self.weight_values)):
            last_data = _datalist[-1]
            try:
                data = float(self.weight_values[i])
            except:
                continue
            
            _datalist.append(data)
            
            ##########  Algorithms Part  ##########
            if (data - total_weight) >= self.save_var.get():  #  record weight
                self.fence_list[-1].piglet_list[-1].weight_list.append(data)
            elif (last_data - data) >= self.save_var.get():  #  pick up pig
                if data < self.save_var.get():
                    total_weight = 0.0
                    f = Fence()
                    self.fence_list.append(f)
            
            # claculate the average
            if(len(self.fence_list[-1].piglet_list[-1].weight_list)) >= 10:
                temp_list = list(self.fence_list[-1].piglet_list[-1].weight_list)
                for i in range(len(temp_list)):
                    temp_list[i] -= total_weight
                    temp_list[i] = round(temp_list[i],2)
                self.fence_list[-1].piglet_list[-1].real_weight_list = temp_list
                self.last_ave = round(mean(temp_list[2:]), 2)
                self.fence_list[-1].piglet_list[-1].weight = self.last_ave
                total_weight += self.last_ave
                self.fence_list[-1].weight = total_weight

                #儲存豬耳號
                # id_list = [self.sow_id.get(),self.pig_id.get()]
                # self.pig_id_list.append(id_list)
                # print(list_to_str(self.pig_id_list))

                p = Pig()  # create a new pig
                self.fence_list[-1].piglet_list.append(p)
                self.fence_list[-1].piglet_num = len(self.fence_list[-1].piglet_list) -1
            
        print("analyze method 2, 10筆data中前2個不計, 後8個算平均")
        x = PrettyTable()
        x.field_names = ["pig","1", "2", "3", "4","5","6","7","8","9","10","weight"]
        for j in range(len(self.fence_list)):
            temp = ["No.",j+1,"Fence","","","","","","","","",""]
            x.add_row(temp)
            for i in range(len(self.fence_list[j].piglet_list)):
                temp = [str(i+1)+"_1"]
                temp.extend(list(self.fence_list[j].piglet_list[i].weight_list))
                temp.append(self.fence_list[j].piglet_list[i].weight)
                while(len(temp) < 12):
                    temp.append("none")
                x.add_row(temp)
                temp = [str(i+1)+"_2"]
                temp.extend(list(self.fence_list[j].piglet_list[i].real_weight_list))
                temp.append(self.fence_list[j].piglet_list[i].weight)
                while(len(temp) < 12):
                    temp.append("none")
                x.add_row(temp)
        print(x)


    def analyze_data3(self):
        # 取10筆data, 算標準差
        _datalist = [0.0]
        self.fence_list = []
        f = Fence()
        self.fence_list.append(f)
        total_weight = 0.0
        for i in range(len(self.weight_values)):
            last_data = _datalist[-1]
            try:
                data = float(self.weight_values[i])
            except:
                continue
            
            _datalist.append(data)
            
            ##########  Algorithms Part  ##########
            if (data - total_weight) >= self.save_var.get():  #  record weight
                self.fence_list[-1].piglet_list[-1].weight_list.append(data)
            elif (last_data - data) >= self.save_var.get():  #  pick up pig
                if data < self.save_var.get():
                    total_weight = 0.0
                    f = Fence()
                    self.fence_list.append(f)
            
            # claculate the weight
            if(len(self.fence_list[-1].piglet_list[-1].weight_list)) >= 10:
                temp_list = list(self.fence_list[-1].piglet_list[-1].weight_list)
                for i in range(len(temp_list)):
                    temp_list[i] -= total_weight
                    temp_list[i] = round(temp_list[i],2)
                self.fence_list[-1].piglet_list[-1].real_weight_list = temp_list
                
                ave = round(mean(temp_list), 2) # 平均
                std_err = round(np.std(temp_list), 2) # 標準差
                self.fence_list[-1].piglet_list[-1].std_err = std_err
                
                #  刪除離群值再取平均
                temp_list_std = []
                for i in range(len(temp_list)):
                    if abs(temp_list[i] - ave)/std_err <= 1:
                        temp_list_std.append(temp_list[i])
                self.fence_list[-1].piglet_list[-1].std_weight_list = temp_list_std
                self.last_ave = round(mean(temp_list_std), 2)

                self.fence_list[-1].piglet_list[-1].weight = self.last_ave
                total_weight += self.last_ave
                self.fence_list[-1].weight = total_weight

                #儲存豬耳號
                # id_list = [self.sow_id.get(),self.pig_id.get()]
                # self.pig_id_list.append(id_list)
                # print(list_to_str(self.pig_id_list))

                p = Pig()  # create a new pig
                self.fence_list[-1].piglet_list.append(p)
                self.fence_list[-1].piglet_num = len(self.fence_list[-1].piglet_list) -1
            
        print("analyze method 3, 10筆data算標準差")
        x = PrettyTable()
        x.field_names = ["pig","1", "2", "3", "4","5","6","7","8","9","10", "std", "weight"]
        for j in range(len(self.fence_list)):
            temp = ["No.",j+1,"Fence","","","","","","","","","",""]
            x.add_row(temp)
            for i in range(len(self.fence_list[j].piglet_list)):
                temp = [str(i+1)+"_1"]
                temp.extend(list(self.fence_list[j].piglet_list[i].weight_list))
                temp.append(self.fence_list[j].piglet_list[i].std_err)
                temp.append(self.fence_list[j].piglet_list[i].weight)
                while(len(temp) < 13):
                    temp.append("none")
                x.add_row(temp)
                temp = [str(i+1)+"_2"]
                temp.extend(list(self.fence_list[j].piglet_list[i].real_weight_list))
                temp.append(self.fence_list[j].piglet_list[i].std_err)
                temp.append(self.fence_list[j].piglet_list[i].weight)
                while(len(temp) < 13):
                    temp.append("none")
                x.add_row(temp)
                temp = [str(i+1)+"_3"]
                temp.extend(list(self.fence_list[j].piglet_list[i].std_weight_list))
                while(len(temp) < 11):
                    temp.append("none")
                temp.append(self.fence_list[j].piglet_list[i].std_err)
                temp.append(self.fence_list[j].piglet_list[i].weight)
                x.add_row(temp)
        print(x)


    def save_setting(self):
        temp = self.save_var.get()
        user_input = sd.askfloat("設定儲存鎖定值", "請輸入儲存鎖定值")
        if user_input is not None:
            self.save_var.set(user_input)
        else:
            self.save_var.set(temp)
        # print("{} {}".format(str_input, type(str_input)))
        self.record_history("設定儲存鎖定值:{}".format(self.save_var.get()))

    def total_weight_setting(self):
        temp = self.total_weight_var.get()
        user_input = sd.askfloat("設定總重鎖定值", "請輸入總重鎖定值")
        if user_input is not None:
            self.total_weight_var.set(user_input)
        else:
            self.total_weight_var.set(temp)
        # print("{}".format(str_input, type(str_input)))
        self.record_history("設定總重鎖定值:{}".format(self.total_weight_var.get()))

    def swine_setting(self):
        user_input = sd.askinteger("設定母豬身分資料", "請輸入母豬身分資料")
        # print("{}".format(str_input, type(str_input)))

    def piglet_setting(self):
        user_input = sd.askinteger("設定仔豬身分資料", "請輸入仔豬身分資料")
        # print("{}".format(str_input, type(str_input)))
    

class mySerialPort:
    def __init__(self, _buadrates):
        self.BAUD_RATES = _buadrates    # 設定傳輸速率
        self.opened = False
    
    def open_port(self, _comport):  #打開串口埠
        self.ser = serial.Serial(_comport, self.BAUD_RATES)   # 初始化序列通訊埠
        self.opened = True
        print("open!\n")
    
    def write_data(self, info):  #寫入資料
        try:
            if self.ser.is_open == True:
                print(str(info))
                self.ser.write(info.encode("utf-8"))
            else:
                print("錯誤")
        except KeyboardInterrupt:
            self.ser.close()    # 清除序列通訊物件
            print('再見！')
    


class Pig():
    def __init__(self):
        self.weight_list = []
        self.real_weight_list = []
        self.std_weight_list = []
        self.weight = 0.0
        self.std_err = 0.0


class Fence():
    def __init__(self):
        self.piglet_num = 0
        self.weight = 0
        self.sow = ""
        self.piglet_list = []
        p = Pig()
        self.piglet_list.append(p)


"""
Tools for displaying tool-tips.
ref: https://github.com/python/cpython/blob/master/Lib/idlelib/tooltip.py
"""
class TooltipBase(object):
    def __init__(self, anchor_widget):
        self.anchor_widget = anchor_widget
        self.tipwindow = None

    def __del__(self):
        self.hidetip()

    def showtip(self):
        if self.tipwindow:
            return
        self.tipwindow = tw = Toplevel(self.anchor_widget)
        tw.wm_overrideredirect(1)
        try:
            # This command is only needed and available on Tk >= 8.4.0 for OSX.
            # Without it, call tips intrude on the typing process by grabbing
            # the focus.
            tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w,
                       "help", "noActivates")
        except TclError:
            pass

        self.position_window()
        self.showcontents()
        self.tipwindow.update_idletasks()  # Needed on MacOS -- see #34275.
        self.tipwindow.lift()  # work around bug in Tk 8.5.18+ (issue #24570)

    def position_window(self):
        x, y = self.get_position()
        root_x = self.anchor_widget.winfo_rootx() + x
        root_y = self.anchor_widget.winfo_rooty() + y
        self.tipwindow.wm_geometry("+%d+%d" % (root_x, root_y))

    def get_position(self):
        """choose a screen position for the tooltip"""
        return 20, self.anchor_widget.winfo_height() + 1

    def showcontents(self):
        raise NotImplementedError

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            try:
                tw.destroy()
            except TclError:  # pragma: no cover
                pass

class OnHoverTooltipBase(TooltipBase):
    def __init__(self, anchor_widget, hover_delay=1000):
        super(OnHoverTooltipBase, self).__init__(anchor_widget)
        self.hover_delay = hover_delay

        self._after_id = None
        self._id1 = self.anchor_widget.bind("<Enter>", self._show_event)
        self._id2 = self.anchor_widget.bind("<Leave>", self._hide_event)
        self._id3 = self.anchor_widget.bind("<Button>", self._hide_event)

    def __del__(self):
        try:
            self.anchor_widget.unbind("<Enter>", self._id1)
            self.anchor_widget.unbind("<Leave>", self._id2)  # pragma: no cover
            self.anchor_widget.unbind("<Button>", self._id3) # pragma: no cover
        except TclError:
            pass
        super(OnHoverTooltipBase, self).__del__()

    def _show_event(self, event=None):
        if self.hover_delay:
            self.schedule()
        else:
            self.showtip()

    def _hide_event(self, event=None):
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self._after_id = self.anchor_widget.after(self.hover_delay,self.showtip)

    def unschedule(self):
        after_id = self._after_id
        self._after_id = None
        if after_id:
            self.anchor_widget.after_cancel(after_id)

    def hidetip(self):
        try:
            self.unschedule()
        except TclError:  # pragma: no cover
            pass
        super(OnHoverTooltipBase, self).hidetip()

class Hovertip(OnHoverTooltipBase):
    def __init__(self, anchor_widget, text, hover_delay=1000):
        super(Hovertip, self).__init__(anchor_widget, hover_delay=hover_delay)
        self.text = text

    def showcontents(self):
        label = Label(self.tipwindow, text=self.text, justify=LEFT,
                    background="#ffffe0", relief=SOLID, borderwidth=1)
        label.pack()



main_window = PigGUI()
main_window.mainloop()
