import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="성비 평균연령 지도", layout="wide")
st.title("🗺️ 남녀 평균연령 차이 시각화 지도")

uploaded_file = st.file_uploader("📂 CSV 업로드 (euc-kr 인코딩)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="cp949")

    # 행정구역 정제 및 성비차이 계산
    df = df[df["행정구역"].str.count(r"\(") == 1].copy()
    df["행정구역명"] = df["행정구역"].str.replace(r"\s*\(.*\)", "", regex=True)
    df["남자 평균연령"] = pd.to_numeric(df["2025년06월_남자 평균연령"], errors="coerce")
    df["여자 평균연령"] = pd.to_numeric(df["2025년06월_여자 평균연령"], errors="coerce")
    df["성비차이"] = df["여자 평균연령"] - df["남자 평균연령"]

    geolocator = Nominatim(user_agent="gender_map")
    df["위도"], df["경도"] = None, None

    with st.spinner("📍 지역 좌표를 불러오는 중입니다..."):
        for i, row in df.iterrows():
            location = geolocator.geocode(row["행정구역명"])
            if location:
                df.at[i, "위도"] = location.latitude
                df.at[i, "경도"] = location.longitude

    df = df.dropna(subset=["위도", "경도"])

    # 지도 생성
    m = folium.Map(location=[36.5, 127.5], zoom_start=7)
    cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        color = "pink" if row["성비차이"] > 0 else "blue"
        label = f"<b>{row['행정구역명']}</b><br>👩 여자 평균연령: {row['여자 평균연령']}<br>👨 남자 평균연령: {row['남자 평균연령']}"
        folium.CircleMarker(
            location=[row["위도"], row["경도"]],
            radius=7,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.6,
            popup=label
        ).add_to(cluster)

    st_folium(m, width=1000, height=700)
