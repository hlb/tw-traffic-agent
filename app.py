import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json

# 設置頁面為寬螢幕模式
st.set_page_config(layout="wide")

# 設置頁面標題
st.title('新竹縣公車站牌資訊')

# 讀取 JSON 資料
@st.cache_data
def load_data():
    with open('data/BusStop_City_HsinchuCounty.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 將資料轉換為 DataFrame
    stops = []
    for stop in data:
        stops.append({
            'StopUID': stop['StopUID'],
            'StopID': stop['StopID'],
            'StopName': stop['StopName']['Zh_tw'],
            'StopAddress': stop.get('StopAddress', ''),
            'Latitude': stop['StopPosition']['PositionLat'],
            'Longitude': stop['StopPosition']['PositionLon']
        })
    return pd.DataFrame(stops)

# 載入資料
df = load_data()

# 建立兩欄位佈局
col1, col2 = st.columns([1, 2])

# 左欄顯示資料表格和統計資訊
with col1:
    st.subheader('站牌列表')
    st.dataframe(df, height=600)
    st.subheader('基本統計')
    st.write(f'總站牌數：{len(df)}')

# 右欄顯示地圖
with col2:
    st.subheader('站牌位置地圖')
    
    # 創建地圖
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], 
                   zoom_start=11,
                   width='100%',
                   height='100%')

    # 在地圖上添加標記
    for idx, row in df.iterrows():
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=row['StopName'],
            tooltip=row['StopName']
        ).add_to(m)

    # 顯示地圖，設置高度為 800 像素
    folium_static(m, width=1200, height=800)
