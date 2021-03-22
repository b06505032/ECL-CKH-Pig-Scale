#!/usr/bin/env python
# coding: utf-8



import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk
from tkinter import simpledialog as sd
from tkinter import filedialog as fd

import serial
import serial.tools.list_ports
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
        self.save_setting()
        self.select_folder()
        #self.total_weight_setting()
        #self.swine_setting()
        #self.piglet_setting()
        self.record_history("initializie!")
        self.data_list = [0.0]
        self.fence_list = []
        self.storage_path = tk.StringVar()
        
    
    def select_folder(self):
        self.storage_path = fd.askdirectory(title = "秤重資料儲存資料夾")
        self.record_history("資料儲存路徑更動:"+self.storage_path)
        print(self.storage_path)
    
    
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
        self.text_history.insert(tk.END, _record_str+"\n"+"\n")
        self.text_history.yview_pickplace("end")

    def setting_frame(self):
        frm_1 = tk.Frame(self)
        frm_1.place(x=10,y=10)
        btn_set1 = tk.Button(frm_1,text="設定儲存鎖定值", command=self.save_setting).grid(row=0,column=0)
        btn_set2 = tk.Button(frm_1,text="設定總重鎖定值",command=self.total_weight_setting).grid(row=0,column=1)
        btn_set3 = tk.Button(frm_1,text="上傳豬隻耳號資料",command=self.select_file).grid(row=1,column=0)
        btn_set4 = tk.Button(frm_1,text="設定資料儲存路徑",command=self.select_folder).grid(row=1,column=1)
        btn_connect = tk.Button(frm_1,command=self.connecting,text="連線").grid(row=0,column=2)
        btn_disconnect = tk.Button(frm_1,text="中斷連線", command=self.disconnect).grid(row=1,column=2)
        
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
            
        lb_sow =  tk.Label(frm_2_up,text="母豬資料")
        lb_sow.grid(row=0,column=0)
        lb_smallpig = tk.Label(frm_2_up,text="仔豬資料").grid(row=0,column=1)
        en_sow = tk.Entry(frm_2_up).grid(row=1,column=0)
        en_smallpig = tk.Entry(frm_2_up).grid(row=1,column=1)
        btn_zero = tk.Button(frm_2_down,text="歸零", command = self.zeroing).grid(row=0,column=0)
        btn_clean = tk.Button(frm_2_down,text="清除上筆").grid(row=0,column=1)

    def weight_frame(self):
        frm_3 = tk.Frame(self)
        frm_3.place(x=450,y=10)
        self.lb_nowshow = tk.Label(frm_3,text="目前秤值").grid(row=0,column=0)
        begin_weigh = tk.Button(frm_3,text="開始秤重",command=weighing).grid(row=0,column=1)
        self.weight_var = tk.StringVar()
        self.weight_var.set(0)
        ####
        # label_weighing_nowshow = tk.Label(frm_3,height=5,textvariable=self.weight_var,width=20)
        # label_weighing_nowshow.grid(row=1,column=0)
        
        self.label_weighing_nowshow = tk.Label(frm_3,height=5,textvariable=self.weight_var,width=20)
        self.label_weighing_nowshow.grid(row=1,column=0)
        
        lb_lastshow = tk.Label(frm_3,text="上筆記錄").grid(row=2,column=0)
        lb_savenum = tk.Label(frm_3,text="已存豬數").grid(row=2,column=1)
        text_weighing_lastshow = tk.Text(frm_3,height=1,width=20).grid(row=3,column=0)
        text_weighing_savenum = tk.Text(frm_3,height=1,width=20).grid(row=3,column=1)

    def record_frame(self):
        frm_4 = tk.Frame(self)
        frm_4.place(x=450,y=200)
        
        setting = tk.Label(frm_4,text="設定內容").grid(row=0,column=1)
        history = tk.Label(frm_4,text="歷史紀錄").grid(row=0,column=2)
        
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
        
        self.status_var, self.save_var, self.total_weight_var = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.status_var.set("disconnect")
        self.save_var.set(0) # 初始值0
        self.total_weight_var.set(0)
        setting1 = tk.Label(setting_entry,width=10,textvariable=self.status_var).grid(row=0, column=0)
        setting2 = tk.Label(setting_entry,width=10,textvariable=self.save_var).grid(row=1, column=0)
        setting3 = tk.Label(setting_entry,width=10,textvariable=self.total_weight_var).grid(row=2, column=0)
        setting4 = tk.Label(setting_entry,width=10).grid(row=3, column=0)
        setting5 = tk.Label(setting_entry,width=10).grid(row=4, column=0)
        setting6 = tk.Label(setting_entry,width=10).grid(row=5, column=0)
        

        # record history
        self.text_history = scrolledtext.ScrolledText(frm_4,height=10,width=20)
        self.text_history.grid(row=1,column=2)


    def zeroing(self):
        self.myserial.write_data("MZ\r\n")
        f = Fence()
        self.fence_list.append(f)

    def connecting(self):
        temp = self.port_var.get()
        try:
            self.myserial.open_port(temp)
            self.zeroing()
            
            self.status_var.set("connect")
            self.record_history("connect")
        except:
            tk.messagebox.showwarning(title=None,message='Error')
        btn_connect.configure(text="中斷連線",command=self.weighing)

    def weighing(self):
         # self.read_data()
        self.label_weighing_nowshow.after(0, self.read_data)

    def disconnect(self):
        self.myserial.ser.close()
        self.record_history("disconnect!")
        self.status_var.set("disconnect")
        btn_connect.configure(text="連線",command=self.connecting)
        

    def read_data(self):  #讀取資料
        if self.myserial.ser.is_open == True:
            # get last data
            last_data = self.data_list[-1]
            print("last data:",last_data)
            
            # read current data
            data_raw = self.myserial.ser.readline()  # 讀取一行
            data = data_raw.decode("utf-8")   # 用預設的UTF-8解碼
            # print('original data:', data_raw)
            data = data.strip("ST,GS,").strip("US,GS,").strip("ST,NT,").strip("ST,TR,").strip("OL,GS")
            data = data.strip().strip("kg").strip("+-")
            if data == "MZ":
                data = 0.0
            data = float(data)  # transfer string to float
            print("data:", data)
            
            self.weight_var.set(data)
            self.data_list.append(data)
            print("data list:", self.data_list)

            #################
            #  Algorithms Part
            if data < float(self.save_var.get()):  # at first no pig
                pass
            elif (data-last_data) > float(self.save_var.get()):  # another pig
                p = Pig()
                self.fence_list[-1].piglet_list.append(p)
                self.fence_list[-1].piglet_list[-1].weight_list.append(self.data_list[-1])
            else:  # same pig
                self.fence_list[-1].piglet_list[-1].weight_list.append(self.data_list[-1])
            #  Algorithms Part

            #################
            #  Degugging Part
            print("Fence num: {}\n".format(len(self.fence_list)))
            if self.fence_list[-1].piglet_list:
                print("Piglet num: {}\n".format(len(self.fence_list[-1].piglet_list)))
                # print("pig weight",self.fence_list[-1].piglet_list[-1].weight_list)
                for i in range(len(self.fence_list[-1].piglet_list)):
                    print("No.", i, "pig")
                    print("weight",self.fence_list[-1].piglet_list[i].weight_list)
            #  Debugging Part

            self.label_weighing_nowshow.after(1000,self.read_data)
            
        else:
            print("serial is not open")

        
    
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
        user_input = sd.askinteger("設定總重鎖定值", "請輸入總重鎖定值")
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
        self.weight = 0


class Fence():
    def __init__(self):
        self.piglet_num = 0
        self.weight = 0
        self.swine = ""
        self.piglet_list = []



main_window = PigGUI()
main_window.mainloop()
