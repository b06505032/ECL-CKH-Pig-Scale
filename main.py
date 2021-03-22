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



class PigGUI(tk.Tk):
    
    def __init__(self):
       
        tk.Tk.__init__(self)
        self.title("仔豬磅秤")
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
        self.datetime_list = []
        self.pig_id_list = []
        self.record_history("initializie!")


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
            print(type(filename))
            with open(filename, newline='') as csvfile:
                rows = csv.reader(csvfile, delimiter=',')
                for row in rows:
                    # print(type(row))
                    print(row[0],row[1])
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
        btn_set1 = tk.Button(frm_1,text="設定儲存鎖定值", command=self.save_setting).grid(row=0,column=0)
        btn_set2 = tk.Button(frm_1,text="秤重資料儲存",command=self.output_csv).grid(row=0,column=1)
        btn_set3 = tk.Button(frm_1,text="上傳豬隻身分資料",command=self.select_file).grid(row=1,column=0)
        btn_set4 = tk.Button(frm_1,text="設定資料儲存路徑",command=self.select_folder).grid(row=1,column=1)
        self.btn_connect = tk.Button(frm_1,command=self.connecting,text="連線")
        self.btn_connect.grid(row=0,column=2)
        btn_weighing = tk.Button(frm_1,text="秤重(平均)", command=self.weighing).grid(row=3,column=0)
        btn_weighing = tk.Button(frm_1,text="秤重(眾數)").grid(row=3,column=1)
        btn_weighing = tk.Button(frm_1,text="秤重(after平均)").grid(row=4,column=0)
        btn_weighing = tk.Button(frm_1,text="秤重(標準差)").grid(row=4,column=1)
        
        port_list = list(serial.tools.list_ports.comports())
        assert (len(port_list) != 0),"无可用串口"
        port_str_list = []
        
        for i in range(len(port_list)):
            # 将串口号切割出来
            lines = str(port_list[i])
            print("port:", i, str(port_list[i]))
            str_list = lines.split(" ")
            port_str_list.append(str_list[0])
        self.port_var = tk.StringVar()
        cbb_com = ttk.Combobox(frm_1,values=port_str_list, textvariable = self.port_var, state="readonly")
        cbb_com.grid(row=2,column=0)
        
        cbb_staff = ttk.Combobox(frm_1,values=["小明","阿嬌"])
        cbb_staff.grid(row=2,column=1)
    
    def data_frame(self):
        frm_2 = tk.Frame(self)
        frm_2.place(x=10,y=200)
        
        frm_2_up = tk.Frame(frm_2)
        frm_2_down = tk.Frame(frm_2)
        frm_2_up.pack(side='top')
        frm_2_down.pack(side='bottom')

        self.sow_id, self.pig_id = tk.StringVar(), tk.StringVar()
        self.sow_id.set("")
        self.pig_id.set("")

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

        setting_entry = tk.LabelFrame(frm_4,padx=5, pady=5)
        setting_entry.grid(row=1, column=1)
        
        self.status_var, self.save_var, self.total_weight_var, self.storage_path_var = tk.StringVar(), tk.DoubleVar(), tk.DoubleVar(), tk.StringVar()
        self.status_var.set("disconnect")
        self.save_var.set(0.0) # 初始值0
        self.total_weight_var.set(0.0)
        self.storage_path_var.set("請選擇資料儲存路徑")
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
        
        
    def connecting(self):
        temp = self.port_var.get()
        try:
            self.myserial.open_port(temp)
            self.zeroing()
            self.status_var.set("connect")
            self.record_history("connect")
            self.btn_connect.configure(text="中斷連線",command=self.disconnect)
        except:
            tk.messagebox.showwarning(title="錯誤",message='請選擇串口埠')


    def disconnect(self):
        self.myserial.ser.close()
        self.record_history("disconnect!")
        self.status_var.set("disconnect")
        self.btn_connect.configure(text="連線",command=self.connecting)
    
    def weighing(self):
        # start reading
        try:
            # create a new fence
            f = Fence()
            self.fence_list.append(f)
            self.label_weighing_nowshow.after(0, self.read_data)
        except AttributeError:
            print("serial is not open!!!!!!!!!!!!")
            tk.messagebox.showwarning(title="錯誤",message='尚未連線!!!!!!!!')


    def output_csv(self):
        file_path = self.storage_path_var.get()
        with open(file_path + "/" + self.today() + "raw data" +'.csv','a+') as log_file:
            logfile = csv.writer(log_file)
            logfile.writerow(self.data_list)
            logfile.writerow(self.datetime_list)

        with open(file_path + "/" + self.today() + "weaned weight" +'.csv','a+') as csv_file:
            write = csv.writer(csv_file)
            header = ["pig id", "time", "weight", "raw data"]
            write.writerow(header)
            for j in range(len(self.fence_list)-1):
                i = len(self.fence_list[j].piglet_list)-1
                k = i*j
                for i in range(len(self.fence_list[j].piglet_list)-1):
                    temp = [self.pig_id_list[k], self.time(),self.fence_list[j].piglet_list[i].weight]
                    temp.extend(self.fence_list[j].piglet_list[i].weight_list)
                    write.writerow(temp)
                    k = k + 1
                temp1 = ["", "", "total", self.fence_list[j].weight]
                write.writerow(temp1)




    def time(self):
        now = datetime.now()
        now_time = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
        return now_time

    def today(self):
        now = datetime.now()
        if len(str(now.month)) == 1:
            month = "0" + str(now.month)
        else:
            month = str(now.month)
        
        if len(str(now.day)) == 1:
            day = "0" + str(now.day)
        else:
            day = str(now.day)
        today = str(now.year) +  month + day
        return today

   

    def read_data(self):  #讀取資料
        if self.myserial.ser.is_open == True:
            # get last data
            last_data = self.data_list[-1]
            # print("last data:",last_data)
            
            # read current data
            data_raw = self.myserial.ser.readline()  # 讀取一行
            data = data_raw.decode("utf-8")   # 用預設的UTF-8解碼
            print('original data:', data_raw)
            data = data.strip("ST,GS,").strip("US,GS,").strip("ST,NT,").strip("ST,TR,").strip("OL,GS")
            data = data.strip().strip("kg").replace(" ", "")
            if data == "MZ":
                data = 0.0
            data = float(data)  # transfer string to float
            print("\ndata:", data)
            
            self.weight_var.set(data)
            self.data_list.append(data)
            self.datetime_list.append(self.time())
            print("data list:", self.data_list)


            ##########  Algorithms Part  ##########
            print("total_weight_var:", self.total_weight_var.get())
            if (data - self.total_weight_var.get()) >= self.save_var.get():  #  record weight
                self.fence_list[-1].piglet_list[-1].weight_list.append(data)
            elif (last_data - data) >= self.save_var.get():  #  pick up pig
                if data < self.save_var.get():
                    self.pig_weight.set("窩重:"+str(self.fence_list[-1].weight))
                    self.record_history("窩重:"+str(self.fence_list[-1].weight))
                    self.total_weight_var.set(0)
                    f = Fence()
                    self.fence_list.append(f)
                    self.zeroing()
                    
            
            # claculate the average
            if(len(self.fence_list[-1].piglet_list[-1].weight_list)) >= 8:
                temp_list = list(self.fence_list[-1].piglet_list[-1].weight_list)
                print("\nrecord weight:", temp_list)
                for i in range(len(temp_list)):
                    temp_list[i] -= self.total_weight_var.get()
                print("calculate weight:", temp_list)
                self.last_ave = mean(temp_list)
                self.fence_list[-1].piglet_list[-1].weight = self.last_ave
                self.total_weight_var.set(round(self.total_weight_var.get()+self.last_ave, 2))
                print("average weight:", round(self.last_ave, 2))
                self.fence_list[-1].weight = self.total_weight_var.get()

                #儲存豬耳號
                id_list = [self.sow_id.get(),self.pig_id.get()]
                self.pig_id_list.append(id_list)
                print(self.pig_id_list)


                # claculate pig number
                if self.fence_list[-1].piglet_list is not []:
                    self.piglet_save_num.set(len(self.fence_list[-1].piglet_list))

                self.pig_weight.set("小豬重: "+str(round(self.fence_list[-1].piglet_list[-1].weight,2)))
                self.record_history("儲存成功!")
                self.record_history("重量："+str(self.fence_list[-1].piglet_list[-1].weight))

                #顯示上頭豬的重量
                #if self.last_ave is not 0.0:
                self.last_piglet_weight.set(round(self.last_ave, 2))
                

                p = Pig()  # create a new pig
                self.fence_list[-1].piglet_list.append(p)
                self.fence_list[-1].piglet_num = len(self.fence_list[-1].piglet_list) -1
                #self.pig_weight.set("")
                





            ##########  Degugging Part  ##########
            print("Total Fence num: {}".format(len(self.fence_list)))
            for j in range(len(self.fence_list)):
                print("No.", j+1, "fence.", "has", len(self.fence_list[j].piglet_list), "pig(s).")
                for i in range(len(self.fence_list[j].piglet_list)):
                    print("No.", i+1, "pig weight:", self.fence_list[j].piglet_list[i].weight_list)
            ##########  Debugging Part  ##########

            self.label_weighing_nowshow.after(500,self.read_data)
        else:
            print("serial is not open")
            tk.messagebox.showwarning(title="錯誤",message='尚未連線')
       
    



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
        
    
    def open_port(self, _comport):  #打開串口埠
        self.ser = serial.Serial(_comport, self.BAUD_RATES)   # 初始化序列通訊埠
        print("open!\n")
    
    
    def write_data(self, info):  #寫入資料
        try:
            if self.ser.is_open == True:
                print(info)
                self.ser.write(info.encode("utf-8"))

            else:
                print("錯誤")
        
        except KeyboardInterrupt:
            self.ser.close()    # 清除序列通訊物件
            print('再見！')
    


class Pig():
    def __init__(self):
        self.weight_list = []
        self.weight = 0.0


class Fence():
    def __init__(self):
        self.piglet_num = 0
        self.weight = 0
        self.sow = ""
        self.piglet_list = []
        p = Pig()
        self.piglet_list.append(p)



main_window = PigGUI()
main_window.mainloop()
