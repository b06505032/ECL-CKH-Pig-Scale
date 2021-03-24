# ECL-CKH-Pig-Scale

## branch description
> 目前 main 與 issue10 為同步
* issue1 - 
* issue2 - 初始版本、可秤重、顯示秤值、紀錄
* issue3 - 新功能：輸出紀錄至csv檔
* issue4
  - 修改csv檔紀錄方式
  - 新功能：輸入母豬仔豬耳號
* issue5 - 新功能：輸出log file、建立三種分析方式
* issue6 - 連線按鈕防呆、速率選單、按鈕懸浮提示窗
* issue7 - GUI畫面樣式更改
* issue8 
  - 修改儲存豬隻csv檔方式
  - 新功能：throw serial exception
* issue9
  - 秤重時間記錄至毫秒、合併"連線"及"開始秤重"(一連線隨即秤重;一停止秤重隨即斷線)
  - 新功能：新增手動秤重(按"決定重量"按鈕來得到該頭小豬重量)
  - 讀取數值與顯示運用multithreading
* issue10
  - 計重方式為利用pandas kpss判斷數據穩定性才計算重量
  - 前後端獨立、版面修改

## 程式架構
* Get to the [report](Pig_Scale_report2.0.pdf) for more detail explination
* 後端
  - Pig: 儲存單隻仔豬資料
  - Fence: 儲存單窩資料
  - Scale: 磅秤
  - SerialThread: 藍芽連線
  - Logger: 紀錄程式執行log檔案
  - Utils: 輔助工具
* 前端
  - GUI: 控制畫面
  - StartView: 起始畫面
  - ScaleView: 秤重畫面
  - AnalyzeView: 分析資料畫面

* Pig
  - weight: 仔豬重量
  - weight_list: 測量重量
  - real_weight_list: 實際重量
  - std_weight_list: 刪除outliers後的重量
  - std_err: 標準差
  - time_list: 所對應的時間
  - kptest: record the return value of the function kpss_test()
  - index: indexing which part of the weight_list passing into the function kpss_test()

* Fence
  - weight: 窩重
  - piglet_num: 小豬數
  - sow: 母豬耳號
  - pig_id: 小豬耳號
  - piglet_list: 所紀錄的小豬

* GUI 畫面呈現、各項功能
  - 連線、中斷連線、設定儲存鎖定值、輸入豬隻耳號、開始秤重、結束秤重、重新分析重量

## 判斷重量方式
1.  取1~40筆資料，取平均
2.  取11~50筆資料，取平均
3.  取1~40筆資料
    計算mean、standard error，
    (data-mean) / stderr > 1 為異端值
    刪除異端值後，取平均
4.  取第11~50筆資料，計算方式同方法3
5.  運用滑動視窗，利用statsmodels中kpss套件計算每一小段數據穩定度，依據穩定度與否決定是否計算平均

## 輸出紀錄檔
每執行一次程式後，會自動輸出紀錄檔
1. time terminal messege (終端機紀錄檔)
2. time data （時間-重量記錄檔）(每新增一個fence，新建一份log) 

## 操作方式-讀取資料做事後分析
- 範例資料檔案: Repo/Doc/1202fence1.log
- 此 [文件](AnalyzeDataManual.md)  說明如何做資料分析
