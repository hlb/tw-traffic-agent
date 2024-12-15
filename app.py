import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import json
import requests

# 設置頁面為寬螢幕模式
st.set_page_config(layout="wide")

# 設置頁面標題
st.title('新竹縣公車站牌資訊')

# 讀取站牌資料
@st.cache_data
def load_stop_data():
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

# 讀取路線資料
@st.cache_data
def load_route_data():
    with open('data/StopOfRoute_HshinchuCounty.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 將資料轉換為更容易使用的格式
    routes = {}
    for route in data:
        route_name = route['RouteName']['Zh_tw']
        route_id = route['RouteUID']
        direction = route.get('Direction', 0)
        
        if route_id not in routes:
            routes[route_id] = {
                'RouteName': route_name,
                'Directions': {}
            }
        
        # 儲存每個方向的站點
        routes[route_id]['Directions'][direction] = [
            {
                'StopUID': stop['StopUID'],
                'StopName': stop['StopName']['Zh_tw'],
                'StopPosition': {
                    'PositionLat': None,  # 稍後從站牌資料填入
                    'PositionLon': None
                }
            }
            for stop in route['Stops']
        ]
    
    return routes

# 載入資料
df_stops = load_stop_data()
routes = load_route_data()

# 建立站牌 UID 到位置的映射
stop_positions = df_stops.set_index('StopUID')[['Latitude', 'Longitude']].to_dict('index')

# 填入站點位置資訊
for route in routes.values():
    for direction_stops in route['Directions'].values():
        for stop in direction_stops:
            if stop['StopUID'] in stop_positions:
                stop['StopPosition']['PositionLat'] = stop_positions[stop['StopUID']]['Latitude']
                stop['StopPosition']['PositionLon'] = stop_positions[stop['StopUID']]['Longitude']

# 建立兩欄位佈局
col1, col2 = st.columns([1, 2])

# 左欄顯示路線選擇和資料表格
with col1:
    # 路線選擇下拉選單
    route_names = [(route_id, info['RouteName']) for route_id, info in routes.items()]
    route_names.sort(key=lambda x: x[1])  # 按路線名稱排序
    selected_route_id = st.selectbox(
        '選擇路線',
        options=[route_id for route_id, _ in route_names],
        format_func=lambda x: next(name for id, name in route_names if id == x)
    )
    
    # 方向選擇
    if selected_route_id:
        directions = routes[selected_route_id]['Directions']
        direction = st.radio(
            '選擇方向',
            options=list(directions.keys()),
            format_func=lambda x: '去程' if x == 0 else '返程'
        )
        
        # 顯示選擇路線的站牌列表
        st.subheader('站牌列表')
        stops_df = pd.DataFrame(directions[direction])
        st.dataframe(stops_df[['StopName']], height=400)

# 右欄顯示地圖
with col2:
    st.subheader('站牌位置地圖')
    
    # 創建地圖
    if selected_route_id:
        # 獲取選擇路線的站點
        route_stops = routes[selected_route_id]['Directions'][direction]
        
        # 計算路線的中心點
        valid_stops = [stop for stop in route_stops if stop['StopPosition']['PositionLat'] is not None]
        center_lat = sum(stop['StopPosition']['PositionLat'] for stop in valid_stops) / len(valid_stops)
        center_lon = sum(stop['StopPosition']['PositionLon'] for stop in valid_stops) / len(valid_stops)
        
        # 創建地圖
        m = folium.Map(location=[center_lat, center_lon], 
                      zoom_start=13,
                      width='100%',
                      height='100%')
        
        # 在地圖上添加站點標記
        for i, stop in enumerate(route_stops, 1):
            if stop['StopPosition']['PositionLat'] is not None:
                # 使用數字作為標記
                folium.CircleMarker(
                    location=[stop['StopPosition']['PositionLat'], 
                             stop['StopPosition']['PositionLon']],
                    radius=10,
                    popup=f"{i}. {stop['StopName']}",
                    tooltip=f"{i}. {stop['StopName']}",
                    color='red',
                    fill=True,
                    fill_color='red'
                ).add_to(m)
        
        # 使用 OSRM 獲取實際路線並繪製
        @st.cache_data
        def get_route_between_points(start_lon, start_lat, end_lon, end_lat):
            url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
            response = requests.get(url)
            if response.status_code == 200:
                route = response.json()
                if "routes" in route and len(route["routes"]) > 0:
                    return route["routes"][0]["geometry"]["coordinates"]
            return None
        
        for i in range(len(valid_stops)-1):
            start = valid_stops[i]
            end = valid_stops[i+1]
            route_coords = get_route_between_points(
                start['StopPosition']['PositionLon'],
                start['StopPosition']['PositionLat'],
                end['StopPosition']['PositionLon'],
                end['StopPosition']['PositionLat']
            )
            
            if route_coords:
                # OSRM 返回的座標是 [lon, lat]，需要轉換為 [lat, lon]
                path_coords = [[coord[1], coord[0]] for coord in route_coords]
                folium.PolyLine(
                    path_coords,
                    weight=3,
                    color='blue',
                    opacity=0.8
                ).add_to(m)
        
    else:
        # 如果沒有選擇路線，顯示所有站點
        m = folium.Map(location=[df_stops['Latitude'].mean(), 
                               df_stops['Longitude'].mean()], 
                      zoom_start=11)
        
        # 在地圖上添加所有站點標記
        for _, row in df_stops.iterrows():
            folium.Marker(
                [row['Latitude'], row['Longitude']],
                popup=row['StopName'],
                tooltip=row['StopName']
            ).add_to(m)

    # 顯示地圖
    folium_static(m, width=1200, height=800)
