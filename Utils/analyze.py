from tkinter import filedialog as fd
from prettytable import PrettyTable
import numpy as np
import pandas as pd
import csv
from Structure.DataStructure import Pig, Fence
from statsmodels.tsa.stattools import kpss
from Utils.Utils import today



def get_record_file():
    filename =  fd.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("log files","*.log"),("all files","*.*")))
    weight_values = []
    time_values = []
    if filename is not None:
        with open(filename, 'r') as file_to_read:
            while True:
                lines = file_to_read.readline()
                if not lines:
                    break
                item = [i for i in lines.split()]
                time_values.append(item[0])                  
                weight_values.append(item[1])
    return filename, weight_values, time_values


def analyze_data1(save_var, sample_size, weight_values, file_path, data_filename):
    if not weight_values:
        return
    _datalist, _fencelist, f = [0.0], [], Fence()
    _fencelist.append(f)
    total_weight = 0.0
    for i in range(len(weight_values)):
        try:
            data = float(weight_values[i])
        except:
            continue
        _datalist.append(data)
        ##########  Algorithms Part  ##########
        if (data - total_weight) >= save_var:  #  record weight
            _fencelist[-1].piglet_list[-1].weight_list.append(data)
        elif (total_weight - data) >= save_var:  #  pick up pig
            if data < save_var:
                total_weight = 0.0
                f = Fence()
                _fencelist.append(f)
        # claculate the average
        if(len(_fencelist[-1].piglet_list[-1].weight_list)) >= sample_size:
            temp_list = list(_fencelist[-1].piglet_list[-1].weight_list)
            for i in range(len(temp_list)):
                temp_list[i] -= total_weight
                temp_list[i] = round(temp_list[i],2)
            _fencelist[-1].piglet_list[-1].real_weight_list = temp_list
            _fencelist[-1].piglet_list[-1].weight = round(np.mean(temp_list),2)
            total_weight += round(np.mean(temp_list),2)
            _fencelist[-1].weight = total_weight
            p = Pig()  # create a new pig
            _fencelist[-1].piglet_list.append(p)
            _fencelist[-1].piglet_num = len(_fencelist[-1].piglet_list) -1 
    x = PrettyTable()
    x.field_names = ["pig"]
    for k in range(1, sample_size+1):
        x.field_names.append(str(k))
    x.field_names.append("weight")
    for i in range(len(_fencelist[0].piglet_list)):
        temp = [str(i+1)+"_measure"]
        temp.extend(list(_fencelist[0].piglet_list[i].weight_list))
        temp.append(_fencelist[0].piglet_list[i].weight)
        while(len(temp) < sample_size + 2):
            temp.append("none")
        x.add_row(temp)
        temp = [str(i+1)+"_calculate"]
        temp.extend(list(_fencelist[0].piglet_list[i].real_weight_list))
        temp.append(_fencelist[0].piglet_list[i].weight)
        while(len(temp) < sample_size + 2):
            temp.append("none")
        x.add_row(temp)
    datafile = open(today()+'.html', 'a', newline='')
    datafile.write(data_filename+'  method1, sample: '+str(sample_size)+x.get_html_string()+'\n===========\n')
    datafile.write('\n')
    datafile.close()
    analyzed_data_output("Method1", file_path, data_filename, _fencelist)


def analyze_data2(save_var, sample_size, weight_values, file_path, data_filename):
    if not weight_values:
        return
    _datalist, _fencelist, f, ss = [0.0], [], Fence(), sample_size+10
    _fencelist.append(f)
    total_weight = 0.0
    for i in range(len(weight_values)):
        try:
            data = float(weight_values[i])
        except:
            continue
        _datalist.append(data)
        ##########  Algorithms Part  ##########
        if (data - total_weight) >= save_var:  #  record weight
            _fencelist[-1].piglet_list[-1].weight_list.append(data)
        elif (total_weight - data) >= save_var:  #  pick up pig
            if data < save_var:
                total_weight = 0.0
                f = Fence()
                _fencelist.append(f)
        # claculate the average
        if(len(_fencelist[-1].piglet_list[-1].weight_list)) >= ss:
            temp_list = _fencelist[-1].piglet_list[-1].weight_list[(ss-sample_size):]
            for i in range(len(temp_list)):
                temp_list[i] -= total_weight
                temp_list[i] = round(temp_list[i],2)
            _fencelist[-1].piglet_list[-1].real_weight_list = [""] * (ss-sample_size)
            _fencelist[-1].piglet_list[-1].real_weight_list.extend(temp_list)
            _fencelist[-1].piglet_list[-1].weight = round(np.mean(temp_list),2)
            total_weight += round(np.mean(temp_list), 2)
            _fencelist[-1].weight = total_weight
            p = Pig()  # create a new pig
            _fencelist[-1].piglet_list.append(p)
            _fencelist[-1].piglet_num = len(_fencelist[-1].piglet_list) -1 
    x = PrettyTable()
    x.field_names = ["pig"]
    for k in range(1, ss + 1):
        x.field_names.append(str(k))
    x.field_names.append("weight")
    for i in range(len(_fencelist[0].piglet_list)):
        temp = [str(i+1)+"_measure"]
        temp.extend(list(_fencelist[0].piglet_list[i].weight_list))
        temp.append(_fencelist[0].piglet_list[i].weight)
        while(len(temp) < ss + 2):
            temp.append("none")
        x.add_row(temp)
        temp = [str(i+1)+"_calculate"]
        temp.extend(list(_fencelist[0].piglet_list[i].real_weight_list))
        temp.append(_fencelist[0].piglet_list[i].weight)
        while(len(temp) < ss + 2):
            temp.append("none")
        x.add_row(temp)
    datafile = open(today()+'.html','a', newline='')
    datafile.write(data_filename + '  method2, sample: '+str(sample_size)+ x.get_html_string()+'\n===========\n')
    datafile.write('\n')
    datafile.close()
    analyzed_data_output("Method2", file_path, data_filename, _fencelist)


def analyze_data3(save_var, sample_size, weight_values, file_path, data_filename):
    if not weight_values:
        return
    _datalist, _fencelist, f = [0.0], [], Fence()
    _fencelist.append(f)
    total_weight = 0.0
    for i in range(len(weight_values)):
        try:
            data = float(weight_values[i])
        except:
            continue
        _datalist.append(data)
        ##########  Algorithms Part  ##########
        if (data - total_weight) >= save_var:  #  record weight
            _fencelist[-1].piglet_list[-1].weight_list.append(data)
        elif (total_weight - data) >= save_var:  #  pick up pig
            if data < save_var:
                total_weight = 0.0
                f = Fence()
                _fencelist.append(f)
        # claculate the average
        if(len(_fencelist[-1].piglet_list[-1].weight_list)) >= sample_size:
            temp_list = list(_fencelist[-1].piglet_list[-1].weight_list)
            for i in range(len(temp_list)):
                temp_list[i] -= total_weight
                temp_list[i] = round(temp_list[i],2)
            _fencelist[-1].piglet_list[-1].real_weight_list = temp_list
            
            # ave = round(mean(temp_list), 2) # 平均
            # std_err = round(std(temp_list), 2) # 標準差
            # _fencelist[-1].piglet_list[-1].std_err = std_err
            ave = np.mean(temp_list)  # 平均
            std_err = np.std(temp_list)  # 標準差
            _fencelist[-1].piglet_list[-1].std_err = round(std_err,2)
            
            #  刪除離群值再取平均
            temp_list_std, _fencelist[-1].piglet_list[-1].mark_std = [], [0] * sample_size
            for i in range(len(temp_list)):
                if abs(temp_list[i] - ave) <= 1*std_err:
                    temp_list_std.append(temp_list[i])
                    _fencelist[-1].piglet_list[-1].mark_std[i] = 1
            _fencelist[-1].piglet_list[-1].std_weight_list = temp_list_std
            last_ave = round(np.mean(temp_list_std), 2)

            _fencelist[-1].piglet_list[-1].weight = last_ave
            total_weight += last_ave
            _fencelist[-1].weight = total_weight
            p = Pig()  # create a new pig
            _fencelist[-1].piglet_list.append(p)
            _fencelist[-1].piglet_num = len(_fencelist[-1].piglet_list) -1
    
    x = PrettyTable()
    x.field_names = ["pig"]
    for k in range(1, sample_size+1):
        x.field_names.append(str(k))
    x.field_names.extend(["std", "weight"])
    for i in range(len(_fencelist[0].piglet_list)):
        if _fencelist[0].piglet_list[0] == 0.0:
            continue
        temp = [str(i+1)+"_measure"]
        temp.extend(list(_fencelist[0].piglet_list[i].weight_list))
        while(len(temp) < sample_size + 3):
            temp.append("none")
        x.add_row(temp)
        temp = [str(i+1)+"_calculate"]
        temp.extend(list(_fencelist[0].piglet_list[i].real_weight_list))
        temp.append(_fencelist[0].piglet_list[i].std_err)
        while(len(temp) < sample_size + 3):
            temp.append("none")
        x.add_row(temp)
        temp = [str(i+1)+"_std"]
        for j in range(len(_fencelist[0].piglet_list[i].real_weight_list)):
            if _fencelist[0].piglet_list[i].mark_std[j] == 0:
                _fencelist[0].piglet_list[i].real_weight_list[j] = '-'
        temp.extend(_fencelist[0].piglet_list[i].real_weight_list)
        # temp.extend(list(_fencelist[0].piglet_list[i].std_weight_list))
        while(len(temp) < sample_size + 1):
            temp.append("none")
        temp.append(_fencelist[0].piglet_list[i].std_err)
        temp.append(_fencelist[0].piglet_list[i].weight)
        x.add_row(temp)
    datafile = open(today()+'.html', 'a', newline='\n')
    datafile.write(data_filename+'  method3, sample: '+str(sample_size)+x.get_html_string()+'\n===========\n')
    datafile.write('\n')
    datafile.close()
    analyzed_data_output("Method3", file_path, data_filename, _fencelist)


def analyze_data4(save_var, sample_size, weight_values, file_path, data_filename):
    if not weight_values:
        return
    _datalist, _fencelist, f, ss = [0.0], [], Fence(), sample_size+10
    _fencelist.append(f)
    total_weight = 0.0
    for i in range(len(weight_values)):
        try:
            data = float(weight_values[i])
        except:
            continue
        _datalist.append(data)
        ##########  Algorithms Part  ##########
        if (data - total_weight) >= save_var:  #  record weight
            _fencelist[-1].piglet_list[-1].weight_list.append(data)
        elif (total_weight - data) >= save_var:  #  pick up pig
            if data < save_var:
                total_weight = 0.0
                f = Fence()
                _fencelist.append(f)
        # claculate the average
        if(len(_fencelist[-1].piglet_list[-1].weight_list)) >= ss:
            temp_list = _fencelist[-1].piglet_list[-1].weight_list[(ss-sample_size):]
            for i in range(len(temp_list)):
                temp_list[i] -= total_weight
                temp_list[i] = round(temp_list[i], 2)
            _fencelist[-1].piglet_list[-1].real_weight_list = [""] * (ss-sample_size)
            _fencelist[-1].piglet_list[-1].real_weight_list.extend(temp_list)
            
            # ave = round(mean(temp_list), 2) # 平均
            # std_err = round(std(temp_list), 2) # 標準差
            # _fencelist[-1].piglet_list[-1].std_err = std_err
            ave = np.mean(temp_list)  # 平均
            std_err = np.std(temp_list)  # 標準差
            _fencelist[-1].piglet_list[-1].std_err = round(std_err,2)
            
            temp_list_std, _fencelist[-1].piglet_list[-1].mark_std = [], [0] * ss
            for i in range(len(temp_list)):
                if abs(temp_list[i] - ave) <= 0.8*std_err:
                    temp_list_std.append(temp_list[i])
                    _fencelist[-1].piglet_list[-1].mark_std[i+(ss-sample_size)] = 1
            _fencelist[-1].piglet_list[-1].std_weight_list = temp_list_std
            last_ave = round(np.mean(temp_list_std), 2)

            _fencelist[-1].piglet_list[-1].weight = last_ave
            total_weight += last_ave
            _fencelist[-1].weight = total_weight
            p = Pig()  # create a new pig
            _fencelist[-1].piglet_list.append(p)
            _fencelist[-1].piglet_num = len(_fencelist[-1].piglet_list) -1 
    
    x = PrettyTable()
    x.field_names = ["pig"]
    for k in range(1, ss+1):
        x.field_names.append(str(k))
    x.field_names.extend(["std", "weight"])
    for i in range(len(_fencelist[0].piglet_list)):
        if _fencelist[0].piglet_list[0] == 0.0:
            continue
        temp = [str(i+1)+"_measure"]
        temp.extend(list(_fencelist[0].piglet_list[i].weight_list))
        while(len(temp) < ss + 3):
            temp.append("none")
        x.add_row(temp)
        temp = [str(i+1)+"_calculate"]
        temp.extend(list(_fencelist[0].piglet_list[i].real_weight_list))
        temp.append(_fencelist[0].piglet_list[i].std_err)
        while(len(temp) < ss + 3):
            temp.append("none")
        x.add_row(temp)
        temp = [str(i+1)+"_std"]
        for j in range(len(_fencelist[0].piglet_list[i].real_weight_list)):
            if j < ss-sample_size:
                continue
            if _fencelist[0].piglet_list[i].mark_std[j] == 0:
                _fencelist[0].piglet_list[i].real_weight_list[j] = '-'
        temp.extend(_fencelist[0].piglet_list[i].real_weight_list)
        while(len(temp) < ss + 1):
            temp.append("none")
        temp.append(_fencelist[0].piglet_list[i].std_err)
        temp.append(_fencelist[0].piglet_list[i].weight)
        x.add_row(temp)
    datafile = open(today()+'.html', 'a', newline='\n')
    datafile.write(data_filename+'  method4, sample: '+str(sample_size)+x.get_html_string()+'\n===========\n')
    datafile.write('\n')
    datafile.close()
    analyzed_data_output("Method4", file_path, data_filename, _fencelist)
    

def kpss_test(series, **kw):    
    statistic, p_value, n_lags, critical_values = kpss(series, **kw)
    return False if p_value < 0.05 else True


def analyze_data5(save_var, sample_size, weight_values, time_values, file_path, data_filename):
    if not weight_values:
        return
    _fencelist, f = [], Fence()
    _fencelist.append(f)
    total_weight = 0.0
    
    for i in range(len(weight_values)):
        data = float(weight_values[i])
        ##########  Algorithms Part  ##########
        if (data - total_weight) >= save_var:  #  record weight
            _fencelist[-1].piglet_list[-1].weight_list.append(data)
            _fencelist[-1].piglet_list[-1].time_list.append(time_values[i])
        elif (total_weight - data) >= save_var:  #  pick up pig
            if data < save_var:
                total_weight = 0.0
                f = Fence()
                _fencelist.append(f)
        
        # claculate the average
        if(len(_fencelist[-1].piglet_list[-1].weight_list)) >= sample_size:
            index = _fencelist[-1].piglet_list[-1].index
            temp_list = _fencelist[-1].piglet_list[-1].weight_list[index:index+sample_size]
            time_list = _fencelist[-1].piglet_list[-1].time_list[index:index+sample_size]
            _fencelist[-1].piglet_list[-1].index += 1
            
            # 原始數據對時間
            ser_data = pd.Series(temp_list, index=time_list)
            temp_test = kpss_test(ser_data)
            _fencelist[-1].piglet_list[-1].kptest.append(1 if temp_test else 0)
            if len(_fencelist[-1].piglet_list[-1].kptest) < 5:
                continue
            if _fencelist[-1].piglet_list[-1].kptest[-5:] != [1]*5:
                continue
            temp_list = _fencelist[-1].piglet_list[-1].weight_list[index-4:index+sample_size]
            time_list = _fencelist[-1].piglet_list[-1].time_list[index-4:index+sample_size]
            ser_data = pd.Series(temp_list, index=time_list)
            temp_list = [round(i-total_weight, 2) for i in temp_list]
            last_ave = round(np.mean(temp_list), 2)
            _fencelist[-1].piglet_list[-1].weight = last_ave
            total_weight += last_ave
            _fencelist[-1].weight = total_weight
            p = Pig()  # create a new pig
            _fencelist[-1].piglet_list.append(p)
            _fencelist[-1].piglet_num = len(_fencelist[-1].piglet_list) - 1
    '''
    print(len(_fencelist))
    for i in range(_fencelist[0].piglet_num):
        print("length:", len(_fencelist[0].piglet_list[i].weight_list))
        print(_fencelist[0].piglet_list[i].weight)
    '''
    analyzed_data_output("Method5", file_path, data_filename, _fencelist)
    


def analyzed_data_output(statistic_method, file_path, data_filename, _fencelist):
    #儲存不同統計方法所得之秤重值，並輸出至csv檔
    with open(file_path + "/" + today() + "analyzed data" +'.csv','a',encoding="utf-8",newline='') as csv_file:
        write = csv.writer(csv_file)
        inner_list = [data_filename, str(statistic_method)]
        for j in range(1):
        # for j in range(len(_fencelist)):
            for i in range(len(_fencelist[j].piglet_list)):
                if _fencelist[j].piglet_list[i].weight is not None:
                    inner_list.append(_fencelist[j].piglet_list[i].weight) 
        analyzed_datalist = [inner_list]
        print(analyzed_datalist)
        output_list = zip(*analyzed_datalist)
        write.writerows(output_list)
    return analyzed_datalist





    