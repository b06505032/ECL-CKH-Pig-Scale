## 程式介面介紹
- 起始介面
![](https://i.imgur.com/JxckQbr.png)
- 進階設定介面
![](https://i.imgur.com/p9ROIH1.png)
- 秤重介面
![](https://i.imgur.com/aDqfmcw.png)
- 分析介面
![](https://i.imgur.com/qn7aWpg.png)

## 分析資料流程
- **Step1: 更改儲存鎖定值**
  - 儲存鎖定值預設值為3
  - 若有需要更改，依照下列說明更改
  - 若不需要更改，則可直接至 Step2
  - “儲存鎖定值”需小於最輕的豬隻重量，例如最輕的豬為3.5公斤，儲存鎖定值可設為3
  - 更改方式
    1. 於起始介面，點擊“進階設定”
       ![](https://i.imgur.com/Oc2HJPR.png)

    2. 點擊“設定儲存鎖定值”
       ![](https://i.imgur.com/7Fq6GhJ.png)

    3. 輸入需要設定的儲存鎖定值後，按下確定。
       ![](https://i.imgur.com/iMUDiXa.png)

    4. 亦可更改分析樣本數(預設值為40)
    5. 關閉進階設定視窗
    6. 回到起始介面
- **Step2: 分析資料**
  - 用於做事後分析歷史資料
  - 範例檔案：Repo/Docs/1202fence1.log
  - 分析方式
    1. 於起始介面，點擊“分析”
    2. 點擊“取得歷史資料”
    3. 選擇檔案位置後開啟
       ![](https://i.imgur.com/EMzcwxR.png)

    4. 將滑鼠滑至分析資料1/2/3/4/5上後，會看到懸浮視窗，說明此種分析之作法
       ![](https://i.imgur.com/FxlL8Ng.png)

    5. 點擊任一個分析方式
    6. 會在程式所在目錄下生成兩份檔案(一為html, 一為csv)
      ![](https://i.imgur.com/mf0vyHr.png)
       - 開起html檔案後可看到測量及運算數據之細節
        ![](https://i.imgur.com/Ye9ykPj.png)

       - 開啟csv檔案後可看到運算結果 
       ![](https://i.imgur.com/qBTNbyi.png)