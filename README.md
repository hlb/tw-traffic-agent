# 新竹縣公車站牌資訊系統 (Hsinchu County Bus Information System)

這是一個使用 Streamlit 開發的網頁應用程式，用於顯示新竹縣的公車站牌資訊和路線資訊。

## 功能特色

- 互動式地圖顯示所有公車站牌位置
- 公車路線資訊查詢
- 站牌詳細資訊顯示
- 路線規劃功能

## 系統需求

- Python 3.8+
- 相關套件 (詳見 requirements.txt)

## 安裝說明

1. 克隆專案到本地：
```bash
git clone [your-repository-url]
cd tw-traffic-agent
```

2. 建立並啟動虛擬環境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安裝相依套件：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 啟動應用程式：
```bash
streamlit run app.py
```

2. 開啟瀏覽器，訪問 http://localhost:8501

## 資料來源

專案使用以下資料檔案：
- `data/BusStop_City_HsinchuCounty.json`: 新竹縣公車站牌資料
- `data/StopOfRoute_HshinchuCounty.json`: 新竹縣公車路線資料

## 相依套件

- streamlit (1.28.2)
- pandas (2.2.3)
- folium (0.15.0)
- streamlit-folium (0.15.0)
- requests (2.31.0)
