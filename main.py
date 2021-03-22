#!/usr/bin/env python
# coding: utf-8


from hovertip import *
from analyze import *
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk
from tkinter import simpledialog as sd
from tkinter import filedialog as fd
from tkinter import *
from datetime import datetime
from serial import SerialException, Serial
import serial.tools.list_ports
from statistics import mean
import csv
import logging
from os import getcwd
import pytz
import threading
import queue
import time as ti
import inspect
import ctypes


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s\'%(msecs)03d %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename='terminal'+today()+'_'+time()+'.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logging.info('Start logging...')
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
        self.geometry("1000x630+200+200")
        self.setting_frame()
        self.weight_frame()
        self.data_frame()
        self.record_frame()
        self.temp_frame()
        self.analysis_frame()
        
        self.queue = queue.Queue()
        self.serialthread = SerialThread(9600, self.queue)
        self.record_list = []
        self.save_setting()
        
        self.data_list = [0.0]
        self.fence_list = []
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
                    print(str(row[0]) +" "+str(row[1]))
        self.record_history("成功上傳豬隻耳號資料")
         

    def record_history(self, _record_str):
        self.record_list.append(_record_str)
        self.text_history.configure(state='normal')
        self.text_history.insert(tk.END, _record_str+"\n")
        self.text_history.yview_pickplace("end")
        self.text_history.configure(state='disabled')
      

    def temp_frame(self):
        frame = ttk.LabelFrame(self,text="測試用")
        frame.place(x=780,y=10)
    
        self.btn_set1 = tk.Button(frame,text="設定儲存鎖定值", command=self.save_setting, font=10)
        self.btn_set1.pack(side=TOP,fill = X, padx=10, pady=5)

        speed = tk.Label(frame,text="紀錄速率", font=10).pack(side=TOP,fill = X, padx=10, pady=5)
        self.ac_rate = tk.IntVar()  # 選擇速率
        cbb_rate = ttk.Combobox(frame,values=[1, 2, 4, 8, 16], textvariable = self.ac_rate, state="readonly", width=12, font=10)
        self.ac_rate.set(16)
        cbb_rate.pack(side=TOP,fill = X, padx=10, pady=5)

        self.sample_size_var = tk.IntVar() #選擇統計分析樣本數
        sample_size = ttk.Combobox(frame,values=[30, 40, 50], textvariable = self.sample_size_var, state="readonly", width=12, font=10)
        self.sample_size_var.set(40)
        sample_size.pack(side=TOP,fill = X, padx=10, pady=5)
 
        btn_get_record_data = tk.Button(frame,text="取得歷史測試資料", command=self.get_record_file, font=10)
        btn_get_record_data.pack(side=TOP,fill = X, padx=10, pady=5)
        self.btn_analyze_data1 = tk.Button(frame,text="分析測試資料1", command=self.analyze_data1, font=10)
        self.btn_analyze_data2 = tk.Button(frame,text="分析測試資料2", command=self.analyze_data2, font=10)
        self.btn_analyze_data3 = tk.Button(frame,text="分析測試資料3", command=self.analyze_data3, font=10)
        self.btn_analyze_data4 = tk.Button(frame,text="分析測試資料4", command=self.analyze_data4, font=10)
        self.btn_analyze_data5 = tk.Button(frame,text="分析測試資料5", command=self.analyze_data5, font=10)
        self.btn_analyze_data_all = tk.Button(frame,text="分析全部", command=self.analyze_data_all, font=10)
        def analyzeBtnSetting(btn: tk.Button, messege: str):
            Hovertip(btn, messege, hover_delay=100)
        analyzeBtnSetting(self.btn_analyze_data1, "直接取平均")
        analyzeBtnSetting(self.btn_analyze_data2, "前幾筆不計，取平均")
        analyzeBtnSetting(self.btn_analyze_data3, "算標準差，刪除異端值，取平均")
        analyzeBtnSetting(self.btn_analyze_data4, "算標準差，前幾筆不計，刪除異端值，取平均")
        analyzeBtnSetting(self.btn_analyze_data5, "利用滑動窗口，判斷數據穩定後，算平均")
        analyzeBtnSetting(self.btn_analyze_data_all, "一次做全部分析方法")
        for btn in [self.btn_analyze_data1, self.btn_analyze_data2, self.btn_analyze_data3, self.btn_analyze_data4, self.btn_analyze_data5, self.btn_analyze_data_all]:
            btn.pack(side=TOP,fill = X, padx=10, pady=5)
            btn.configure(state=DISABLED)

        
    def setting_frame(self):
        frm_1 = ttk.LabelFrame(self,text="一般設定")
        frm_1.place(x=15,y=10)
        
        #取得串口埠
        port_list = list(serial.tools.list_ports.comports())
        assert (len(port_list) != 0),"無可用串口"
        port_str_list = []
        for i in range(len(port_list)):
            lines = str(port_list[i])
            print("port: " + str(i) + " " + str(port_list[i]))
            str_list = lines.split(" ")
            port_str_list.append(str_list[0])

        self.port_var = tk.StringVar()
        self.port_var.set("請選擇連線串口埠")
        cbb_com = ttk.Combobox(frm_1,values=port_str_list, textvariable = self.port_var, state="readonly", width=15, font=20)
        cbb_com.pack(side=TOP,fill = X, padx=10, pady=5)

        self.mode_var = tk.StringVar()
        self.mode_var.set("自動模式")
        self.cbb_mode = ttk.Combobox(frm_1,values=["自動模式","手動模式"],textvariable = self.mode_var,state="readonly", width=15, font=20)
        self.cbb_mode.pack(side=TOP,fill = X, padx=10, pady=5)

        self.btn_weighing = tk.Button(frm_1,command=self.weighing,text="開始秤重", font=20)
        self.btn_weighing.pack(side=TOP,fill = X, padx=10, pady=5)
        self.btn_set4 = tk.Button(frm_1,text="設定資料儲存路徑",command=self.select_folder, font=20)
        self.btn_set4.pack(side=TOP,fill = X, padx=10, pady=5)
        self.btn_set2 = tk.Button(frm_1,text="秤重資料儲存",command=self.output_csv, font=20)
        self.btn_set2.pack(side=TOP,fill = X, padx=10, pady=5)
       
        cbb_staff = ttk.Combobox(frm_1,values=["小明","阿嬌"], width=12, font=20)
        cbb_staff.pack(side=TOP,fill = X, padx=10, pady=5)


    def change_color(self, event): #點擊widget時，改變其顏色
        widget = self.frm_2.focus_get()
        if self.en_sow['fg']=="red" and str(widget) == ".!labelframe2.!entry":
            self.input_sow_id.set("")
            self.en_sow.configure(font=("Calibri",33),width=8, fg="black")
        elif self.en_piglet['fg']=="red" and str(widget) == ".!labelframe2.!entry2":
            self.input_piglet_id.set("")
            self.en_piglet.configure(font=("Calibri",33),width=8, fg="black")

        
    def data_frame(self):
        self.frm_2 = ttk.LabelFrame(self,text="耳號設定", relief=RIDGE)
        self.frm_2.place(x=15,y=325)
        
        self.input_sow_id, self.input_piglet_id = tk.StringVar(), tk.StringVar()
        self.input_sow_id.set("請輸入耳號")
        self.input_piglet_id.set("請輸入耳號")

        lb_sow =  tk.Label(self.frm_2,text="母豬耳號", font=13)
        lb_sow.pack(side=TOP, padx=10, pady=5, anchor=tk.W)
        self.en_sow = tk.Entry(self.frm_2, textvariable = self.input_sow_id, font=("Calibri",26),width=10, fg="red")
        self.en_sow.pack(side=TOP, padx=10, pady=5,ipady=3)
        self.bind("<Button-1>", lambda e: self.change_color(e))
        
        lb_piglet = tk.Label(self.frm_2,text="仔豬耳號", font=13)
        lb_piglet.pack(side=TOP, padx=10, pady=5, anchor=tk.W)
        self.en_piglet = tk.Entry(self.frm_2, textvariable = self.input_piglet_id, font=("Calibri",26),width=10, fg="red")
        self.en_piglet.pack(side=TOP, padx=10, pady=5,ipady=3)

        self.btn_set3 = tk.Button(self.frm_2,text="上傳豬隻身分資料",command=self.select_file, font=20)
        self.btn_set3.pack(side=TOP, padx=10, pady=5, fill=X)

    
    def decide_weight(self):
        self.btn_decide_weight.focus_set()

    
    def weight_frame(self):
        frm_3 = tk.Frame(self, bd=1, padx=10, pady=10, relief=RAISED)
        frm_3.place(x=250,y=15)
    
        self.weight_var = tk.StringVar()
        self.weight_var.set("0.0kg")
        lb_current_weight = tk.Label(frm_3,text="目前秤值",font=20)
        lb_current_weight.pack(side=TOP,anchor=tk.W)
        self.label_weighing_nowshow = tk.Label(frm_3,textvariable=self.weight_var,font=("Calibri",90),bd=2,anchor=tk.E,width=7,height=1,bg="white",fg="black",padx=10)
        self.label_weighing_nowshow.pack(side=TOP,pady=5,fill = X)
        
        sub_frm = tk.Frame(frm_3, padx=10, pady=4)
        btn_zero = tk.Button(sub_frm,text="歸零", command = self.zeroing, font=20)
        btn_zero.pack(side=RIGHT,pady=4,anchor=tk.E)
        self.btn_decide_weight = tk.Button(sub_frm,text="決定重量", font=10, command=self.decide_weight)
        self.btn_decide_weight.pack(side=RIGHT,padx=5,pady=4,anchor=tk.E)
        sub_frm.pack(side=TOP,fill = X)
        
        self.piglet_save_num, self.litter_weight, self.piglet_weight = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.piglet_save_num.set("已存豬數：0")
        self.litter_weight.set("0.0kg")
        self.piglet_weight.set("0.0kg")

        lb_pig_weight = tk.Label(frm_3,text="仔豬重",font=20)
        lb_pig_weight.pack(side=TOP,anchor=tk.W)
        self.pig_weight_show = tk.Label(frm_3,textvariable=self.piglet_weight,font=("Calibri",60),bd=1,anchor=tk.W,bg="gray77",fg="gray77",padx=10,width=11,height=1)
        self.pig_weight_show.pack(side=TOP,pady=5)
        
        lb_litter_weighing = tk.Label(frm_3,text="窩重",font=20)
        lb_litter_weighing.pack(side=TOP,anchor=tk.W)
        self.litter_weighing_show = tk.Label(frm_3,textvariable=self.litter_weight,font=("Calibri",60),bd=1,anchor=tk.W,bg="gray77",fg="gray77",padx=10,width=11,height=1)
        self.litter_weighing_show.pack(side=TOP,pady=5)


    def analysis_frame(self):
        frame = tk.Frame(self, bd=1, padx=10, pady=5)
        frame.place(x=627,y=565)
        btn_analysis = tk.Button(frame,text="資料分析", font=20)
        btn_analysis.pack(side=TOP, anchor=tk.E)
    
    
    def record_frame(self):
        frm_4 = tk.Frame(self, bg="#DCDCDC")
        frm_4.place(x=780,y=420)
        
        setting = tk.Label(frm_4,text="設定內容")
        setting.grid(row=0,column=1)
        
        setting_context = tk.LabelFrame(frm_4,padx=2, pady=2)
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
        self.storage_path_var.set(getcwd())
        setting1 = tk.Label(setting_entry,width=10,textvariable=self.status_var).grid(row=0, column=0)
        setting2 = tk.Label(setting_entry,width=10,textvariable=self.save_var).grid(row=1, column=0)
        setting3 = tk.Label(setting_entry,width=10,textvariable=self.total_weight_var).grid(row=2, column=0)
        setting4 = tk.Label(setting_entry,width=10).grid(row=3, column=0)
        setting5 = tk.Label(setting_entry,width=10,textvariable=self.storage_path_var).grid(row=4, column=0)
        setting6 = tk.Label(setting_entry,width=10).grid(row=5, column=0)

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
        self.serialthread.write_data("MZ\r\n")
        self.weight_var.set(0.0)


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


    def weighing(self):
        # open and connect port
        temp = self.port_var.get()
        try:
            self.serialthread.open_port(temp)
            self.status_var.set("connect")
            self.record_history("連線")
            self.btn_weighing.configure(state=NORMAL)
        except:
            tk.messagebox.showwarning(title="錯誤",message='請選擇串口埠')
            return
        if self.serialthread.ser.is_open:
            self.zeroing()
            self.datafile = open(today()+'_'+time()+'.log',"w")
            # strat the thread
            self.serialthread.start()
            self.read_data()
            f = Fence() # create a new fence
            self.fence_list.append(f)
            self.record_history("開始秤重")
            self.btn_weighing.configure(text = "結束並儲存",command=self.stop_weighing)
            self.btn_set1.configure(state = DISABLED)
            self.btn_set2.configure(state = DISABLED)
            self.btn_set3.configure(state = DISABLED)
            self.btn_set4.configure(state = DISABLED)
            if self.mode_var.get() == "自動模式":
                self.btn_decide_weight.configure(state = DISABLED)
            elif self.mode_var.get() == "手動模式":
                self.btn_decide_weight.configure(state = NORMAL)
            self.cbb_mode.configure(state = DISABLED)
        else:
            print("serial is not open!!!!!!!!!!!!")
            tk.messagebox.showwarning(title="錯誤",message='尚未連線!!!!!!!!')

    
    def stop_weighing(self):
        self.label_weighing_nowshow.after_cancel(self.weight_value_show)
        # stop the thread
        self.serialthread.ser.reset_input_buffer()
        self._async_raise(self.serialthread.ident, SystemExit)
        self.serialthread.join()
        print("Stopped!")
        self.record_history("停止秤重")
        # close the datafile, output to csv
        self.datafile.close()
        self.data_list = [0.0]
        # close the serial port
        self.serialthread.ser.close()
        self.record_history("中斷連線")
        self.status_var.set("disconnect")
        # reset button state
        self.btn_weighing.configure(text = "開始秤重",command=self.weighing)
        btn_list = [self.btn_set1, self.btn_set2, self.btn_set3, self.btn_set4, self.btn_decide_weight, self.cbb_mode]
        for btn in btn_list:
            btn.configure(state = NORMAL)
        self.output_csv()
        print("===STOP WEIGHTING DEBUG PART===")
        print(len(self.fence_list))
        for i in range(self.fence_list[0].piglet_num):
            print("length: " +str(len(self.fence_list[0].piglet_list[i].weight_list)))
            print(self.fence_list[0].piglet_list[i].weight)
        print("===STOP WEIGHTING DEBUG PART===")
        

    def output_csv(self):
        file_path = self.storage_path_var.get()#取路徑的資料
        with open(file_path + "/" + today() + "weaned weight" +'.csv','a+',encoding="utf-8",newline='') as csv_file:
            write = csv.writer(csv_file)
            header = ["sow id", "piglet id", "weight","fence weight","number born alive"]
            write.writerow(header)
            print("===OUTPUT CSV DEBUG PART===")
            for j in range(len(self.fence_list)-1):
                print("fence_weight: "+str(self.fence_list[j].weight)) # 印在終端機的
                if self.fence_list[j].weight is not None:
                    for i in range(len(self.fence_list[j].piglet_list)-1):
                        print("pig_weight: "+str(self.fence_list[j].piglet_list[i].weight))
                        temp = self.fence_list[j].pig_id[i] # [母豬，小豬]
                        temp.append(str(self.fence_list[j].piglet_list[i].weight)) # [母豬，小豬，小豬重量]
                        print(list_to_str(temp)) # 印在終端機的
                        write.writerow(temp)
                temp1 = ["", "", "", self.fence_list[j].weight, len(self.fence_list[j].piglet_list)-1]
                write.writerow(temp1)
            print("===OUTPUT CSV DEBUG PART===")


    def read_data(self):  #讀取資料
        value = True
        while self.queue.qsize():
            try:  # get data from queue
                data = self.queue.get()
                print("original data: "+ str(data))
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
                        self.data_list.append(data)
                        local_dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei'))
                        currentTime = pytz.timezone('Asia/Taipei').normalize(local_dt).strftime('%H:%M:%S\'%f')[:-3]
                        self.datafile.write(currentTime + " " + str(data) + "\n")

                        ##########  Algorithms Part  ##########
                        if (data - self.total_weight_var.get()) >= self.save_var.get():  #  record weight
                            self.fence_list[-1].piglet_list[-1].weight_list.append(data)
                            self.pig_weight_show.configure(bg="gray77",fg="gray77")
                            self.litter_weighing_show.configure(bg="gray77",fg="gray77")
                        elif (self.total_weight_var.get() - data) >= self.save_var.get():  #  pick up pig
                            if data < self.save_var.get() and data >=0:
                                self.litter_weight.set(str(round(self.fence_list[-1].weight,2))+"kg")
                                self.litter_weighing_show.configure(bg="white",fg="black")
                                self.record_history("窩重:"+str(self.fence_list[-1].weight))
                                self.en_sow.configure(font=("Calibri",26),width=10, fg="red")
                                self.input_sow_id.set("請輸入耳號")
                                self.total_weight_var.set(0)
                                self.datafile.close()
                                self.datafile = open(today()+'_'+time()+'.log',"w")
                                f = Fence()
                                self.fence_list.append(f)
                                self.zeroing()
                        # claculate the average
                        statement = False  #自動/手動決定重量有不同的判斷式
                        if (len(self.fence_list[-1].piglet_list[-1].weight_list)) >= self.sample_size_var.get():
                            if self.mode_var.get() == "自動模式":
                                statement = True
                        if str(self.focus_get()) == ".!frame.!frame.!button2":
                            if self.mode_var.get() == "手動模式":
                                statement = True
                                local_dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Taipei'))
                                tmp = pytz.timezone('Asia/Taipei').normalize(local_dt).strftime('%H:%M:%S\'%f')[:-3] +  " press_decide_weight_button\n"
                                self.datafile.write(tmp) #記錄按按鈕的時間
                        if statement:
                            self.btn_set1.focus_set()
                            temp_list = list(self.fence_list[-1].piglet_list[-1].weight_list)
                            # print("record weight: " + list_to_str(temp_list))
                            for i in range(len(temp_list)):
                                temp_list[i] -= self.total_weight_var.get()
                            # print("calculate weight: "+ list_to_str(temp_list))
                            last_ave = round(mean(temp_list),2)
                            self.fence_list[-1].piglet_list[-1].weight = last_ave
                            self.total_weight_var.set(self.total_weight_var.get()+last_ave)
                            self.fence_list[-1].weight = self.total_weight_var.get()

                            # 儲存豬耳號
                            temp_ID=[self.input_sow_id.get() ,self.input_piglet_id.get()]
                            self.fence_list[-1].pig_id.append(temp_ID)

                            # claculate pig number
                            if self.fence_list[-1].piglet_list is not []:
                                self.piglet_save_num.set("已存豬數："+str(len(self.fence_list[-1].piglet_list)))
                                self.fence_list[-1].piglet_num = len(self.fence_list[-1].piglet_list)
                            # show information
                            self.piglet_weight.set(str(round(self.fence_list[-1].piglet_list[-1].weight,2))+"kg")
                            self.pig_weight_show.configure(bg="white",fg="black")
                            self.record_history("儲存成功!")
                            self.record_history("重量："+str(self.fence_list[-1].piglet_list[-1].weight))
                            self.en_piglet.configure(font=("Calibri",26),width=10, fg="red")
                            self.input_piglet_id.set("請輸入耳號")
                            # create a new pig
                            p = Pig()
                            self.fence_list[-1].piglet_list.append(p)
            except queue.Empty:
                pass
        self.weight_value_show = self.label_weighing_nowshow.after(100, self.read_data)
        
    
    def get_record_file(self):
        self.data_filename, self.weight_values, self.time_values = get_record_file()
        self.record_history("取得歷史資料: " + self.data_filename)
        btn_list = [self.btn_analyze_data1, self.btn_analyze_data2, self.btn_analyze_data3, self.btn_analyze_data4, self.btn_analyze_data5, self.btn_analyze_data_all]
        for btn in btn_list:
            btn.configure(state=NORMAL)
        
    
    def analyze_data1(self):
        print(f'analyze method 1 取{self.sample_size_var.get()}筆data, 直接算平均')
        analyze_data1(self.save_var.get(), self.sample_size_var.get(), self.weight_values, self.storage_path_var.get(), self.data_filename)
        
    
    def analyze_data2(self):
        print(f'analyze method 2 取{self.sample_size_var.get()}筆data, 前 n比不計, 算平均')
        analyze_data2(self.save_var.get(), self.sample_size_var.get(), self.weight_values, self.storage_path_var.get(), self.data_filename)


    def analyze_data3(self):
        print(f'analyze method 3 取{self.sample_size_var.get()}筆data, 刪除離群值, 算平均')
        analyze_data3(self.save_var.get(), self.sample_size_var.get(), self.weight_values, self.storage_path_var.get(), self.data_filename)
    

    def analyze_data4(self):
        print(f'analyze method 4 取{self.sample_size_var.get()}筆data, 前 n比不計, 刪除離群值, 算平均')
        analyze_data4(self.save_var.get(), self.sample_size_var.get(), self.weight_values, self.storage_path_var.get(), self.data_filename)


    def analyze_data5(self):
        print(f'analyze method 5 利用滑動窗口，判斷數據穩定後，算平均')
        analyze_data5(self.save_var.get(), self.sample_size_var.get(), self.weight_values, self.time_values, self.storage_path_var.get(), self.data_filename)


    def analyze_data_all(self):
        self.analyze_data1()
        self.analyze_data2()
        self.analyze_data3()
        self.analyze_data4()
        self.analyze_data5()


    def save_setting(self):
        temp = self.save_var.get()
        user_input = sd.askfloat("設定儲存鎖定值", "請輸入儲存鎖定值")
        if user_input is not None:
            self.save_var.set(user_input)
        else:
            self.save_var.set(temp)
        self.record_history("設定儲存鎖定值:{}".format(self.save_var.get()))


    def total_weight_setting(self):
        temp = self.total_weight_var.get()
        user_input = sd.askfloat("設定總重鎖定值", "請輸入總重鎖定值")
        if user_input is not None:
            self.total_weight_var.set(user_input)
        else:
            self.total_weight_var.set(temp)
        self.record_history("設定總重鎖定值:{}".format(self.total_weight_var.get()))
    

class SerialThread(threading.Thread):
    def __init__(self, _buadrates, _queue):
        threading.Thread.__init__(self)
        self.queue = _queue
        self.BAUD_RATES = _buadrates
    
    def open_port(self, _comport):
        self.ser = Serial(_comport, self.BAUD_RATES, timeout=1)

    def write_data(self, info):  #寫入資料
        if self.ser.is_open == True:
            print("serial writing data:"+str(info))
            self.ser.write(info.encode("utf-8"))
        else:
            print("錯誤")

    def start(self):
        threading.Thread.__init__(self)
        threading.Thread.start(self)

    def run(self):
        # s.write(str.encode('*00T%'))
        ti.sleep(0.2)
        while True:
            if self.ser.in_waiting:
                try:
                    text = self.ser.readline()
                    self.queue.put(text)
                except SerialException as e:
                    print("Serial exception: " + str(e))
                    pass

main_window = PigGUI()
main_window.mainloop()
