from tkinter import ttk
import tkinter as tk
from tkinter import *
from Utils.hovertip import *
from Utils.analyze import *
from os import getcwd
from Utils.Logger import print

class AnalyzeView(tk.Frame):
    def __init__(self, parent, controller, system):
        tk.Frame.__init__(self, parent)
        self.system = system
        
        label = tk.Label(self, text="Analyze")
        label.pack(side="top", fill="x", pady=10)

        btn_get_record_data = tk.Button(self,text="取得歷史測試資料", command=self.get_record_file, font=10)
        btn_get_record_data.pack(side=TOP,fill = X, padx=10, pady=5)
        self.btn_analyze_data1 = tk.Button(self, text="分析測試資料1", command=self.analyze_data1, font=10)
        self.btn_analyze_data2 = tk.Button(self, text="分析測試資料2", command=self.analyze_data2, font=10)
        self.btn_analyze_data3 = tk.Button(self, text="分析測試資料3", command=self.analyze_data3, font=10)
        self.btn_analyze_data4 = tk.Button(self, text="分析測試資料4", command=self.analyze_data4, font=10)
        self.btn_analyze_data5 = tk.Button(self, text="分析測試資料5", command=self.analyze_data5, font=10)
        self.btn_analyze_data_all = tk.Button(self, text="分析全部", command=self.analyze_data_all, font=10)
        def analyzeBtnHover(btn: tk.Button, messege: str):
            Hovertip(btn, messege, hover_delay=100)
        analyzeBtnHover(self.btn_analyze_data1, "直接取平均")
        analyzeBtnHover(self.btn_analyze_data2, "前幾筆不計，取平均")
        analyzeBtnHover(self.btn_analyze_data3, "算標準差，刪除異端值，取平均")
        analyzeBtnHover(self.btn_analyze_data4, "算標準差，前幾筆不計，刪除異端值，取平均")
        analyzeBtnHover(self.btn_analyze_data5, "利用滑動窗口，判斷數據穩定後，算平均")
        analyzeBtnHover(self.btn_analyze_data_all, "一次做全部分析方法")
        for btn in [self.btn_analyze_data1, self.btn_analyze_data2, self.btn_analyze_data3, self.btn_analyze_data4, self.btn_analyze_data5, self.btn_analyze_data_all]:
            btn.pack(side=TOP,fill = X, padx=10, pady=5)
            btn.configure(state=DISABLED)

        button = tk.Button(self, text="Go to the home page",
                           command=lambda: controller.show_frame("StartView", self.system))
        button.pack()
    

    def get_record_file(self):
        self.data_filename, self.weight_values, self.time_values = get_record_file()
        print("取得歷史資料: " + self.data_filename)
        btn_list = [self.btn_analyze_data1, self.btn_analyze_data2, self.btn_analyze_data3, self.btn_analyze_data4, self.btn_analyze_data5, self.btn_analyze_data_all]
        for btn in btn_list:
            btn.configure(state=NORMAL)


    def analyze_data1(self):
        print(f'analyze method 1 取{self.system.sampleSize}筆data, 直接算平均')
        # analyze_data1(self.system.threshold, self.system.sampleSize, self.weight_values, self.storage_path_var.get(), self.data_filename)
        analyze_data1(self.system.threshold, self.system.sampleSize, self.weight_values, getcwd(), self.data_filename)
        
    
    def analyze_data2(self):
        print(f'analyze method 2 取{self.system.sampleSize}筆data, 前 n比不計, 算平均')
        # analyze_data2(self.system.threshold, self.system.sampleSize, self.weight_values, self.storage_path_var.get(), self.data_filename)
        analyze_data2(self.system.threshold, self.system.sampleSize, self.weight_values, getcwd(), self.data_filename)


    def analyze_data3(self):
        print(f'analyze method 3 取{self.system.sampleSize}筆data, 刪除離群值, 算平均')
        # analyze_data3(self.system.threshold, self.system.sampleSize, self.weight_values, self.storage_path_var.get(), self.data_filename)
        analyze_data3(self.system.threshold, self.system.sampleSize, self.weight_values, getcwd(), self.data_filename)
    

    def analyze_data4(self):
        print(f'analyze method 4 取{self.system.sampleSize}筆data, 前 n比不計, 刪除離群值, 算平均')
        # analyze_data4(self.system.threshold, self.system.sampleSize, self.weight_values, self.storage_path_var.get(), self.data_filename)
        analyze_data4(self.system.threshold, self.system.sampleSize, self.weight_values, getcwd(), self.data_filename)


    def analyze_data5(self):
        print(f'analyze method 5 利用滑動窗口，判斷數據穩定後，算平均')
        # analyze_data5(self.system.threshold, self.system.sampleSize, self.weight_values, self.time_values, self.storage_path_var.get(), self.data_filename)
        analyze_data5(self.system.threshold, self.system.sampleSize, self.weight_values, self.time_values, getcwd(), self.data_filename)


    def analyze_data_all(self):
        self.analyze_data1()
        self.analyze_data2()
        self.analyze_data3()
        self.analyze_data4()
        self.analyze_data5()

