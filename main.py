import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# 페이지 설정
st.set_page_config(page_title="📍 나만의 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도")
st.caption("주소를 입력하거나 지도를 클릭하여 북마크를 추가하고, 원하는 색상과 아이콘도 설정하세요!")

# 세션 상태 초기화
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []

# 기본 위치 (서울)
default_location = [37.5665, 126.9780]

# 마커 색상/아이콘 옵션
colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightblue", "black"]
icons = ["info-sign", "home", "star", "flag", "cloud", "heart", "gift", "leaf"]

# --- 북마크 추가: 주소 입력 폼 ---
with st.form("address_form"):
    st.subheader("🏠 주소로 북마크 추가")
    address = st.text_input("주소 입력 (예: 서울특별시 중구 세종대로 110)", key="addr_input")
    name = st.text_input("📌 북마크 이름", key="addr_name")
    color = st.selectbox("🎨 마커 색상 선택", colors, key="addr_color")
    icon = st.selectbox("🔰 아이콘 선택", icons, key="addr_icon")
    submit = st.form_submit_button("주소로 북마크 추가")

    if submit and address.strip() and name.strip():
        geolocator = Nominatim(user_agent="my_map_app")
        location = geolocator.geocode(address)
        if location:
            coords = [location.latitude, location.longitude]
            st.session_state.bookmarks.append({
                "name": name.strip(),
                "coords": coords,
                "color": color,
                "icon": icon
            })
            st.success(f"📍 주소 변환 완료: {coords}")
            st.experimental_rerun()
        else:
            st.error("❌ 주소를 찾을 수 없습니다. 정확히 입력했는지 확인해주세요.")

# --- 북마크 목록 표시 ---
if st.session_state.bookmarks:
    st.markdown("---")
    st.subheader("📚 북마크 목록")
    for i, bm in enumerate(st.session_state.bookmarks, start=1):
        st.write(f"{i}. {bm['name']} - ({bm['coords'][0]:.4f}, {bm['coords'][1]:.4f}) / 색상: {bm['color']}, 아이콘: {bm['icon']}")

    if st.button("🔄 북마크 전체 초기화"):
        st.session_state.bookmarks = []
        st.experimental_rerun()
else:
    st.info("북마크가 없습니다. 주소를 입력하거나 지도를 클릭하여 추가해보세요.")

# --- 지도 생성 ---
# folium 지도 객체 생성
m = folium.Map(location=default_location, zoom_start=12)

# 기존 북마크 마커 표시
for bm in st.session_state.bookmarks:
    folium.Marker(
        location=bm["coords"],
        popup=bm["name"],
        icon=folium.Icon(color=bm["color"], icon=bm["icon"], prefix="fa")
    ).add_to(m)

# 지도 클릭 이벤트 감지
map_data = st_folium(m, width=700, height=500)

# 지도 클릭 시 북마크 추가 폼 (지도 아래에 위치하도록)
if map_data and map_data["last_clicked"]:
    clicked = map_data["last_clicked"]
    st.success(f"🖱️ 클릭한 위치: {clicked}")

    with st.form("map_click_form"):
        name = st.text_input("📌 북마크 이름", key="click_name")
        color = st.selectbox("🎨 마커 색상 선택", colors, key="click_color")
        icon = st.selectbox("🔰 아이콘 선택", icons, key="click_icon")
        submit = st.form_submit_button("지도로 북마크 추가")

        if submit and name.strip():
            st.session_state.bookmarks.append({
                "name": name.strip(),
                "coords": [clicked["lat"], clicked["lng"]],
                "color": color,
                "icon": icon
            })
            st.experimental_rerun()
