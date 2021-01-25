# mylinebot

## 爬取中油提供公開資訊，提供使用者透過Line查詢
功能如下:
* 查詢即時油價
* 爬取歷史油價繪製圖
* 查詢中油加油站點(可選擇條件)
* 訂閱每週油價漲跌
* 計算油價與公升轉換
* 查詢Gogoro電池交換站

## 使用技術
* 此專案是使用 python + django + django_rest_framework框架完成
* 爬取透過中油提供API + requests + xml + json 資料處理分析
* 資料庫使用 sqlite3
* 繪圖使用 pyecharts
* 訊息透過 Linebot + LineNotify


