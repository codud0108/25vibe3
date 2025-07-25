import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(page_title="📍 Bookmark Map", layout="wide")
st.title("📍 나만의 북마크 지도")
st.caption("주소 입력 또는 지도 클릭으로 북마크 추가. 색상과 아이콘 선택 가능!")

if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []

default_location = [37.5665, 126.9780]
colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightblue", "black"]
icons = ["info-sign", "home", "star", "flag", "cloud", "heart", "gift", "leaf"]

# 주소 입력 폼
with st.form("address_form"):
    st.subheader("🏠 주소로 북마크 추가")
    address = st.text_input("주소 입력", key="addr_addr")
    name_addr = st.text_input("북마크 이름", key="addr_name")
    color_addr = st.selectbox("마커 색상", colors, key="addr_color")
    icon_addr = st.selectbox("아이콘", icons, key="addr_icon")
    submitted_addr = st.form_submit_button("주소로 추가")
    if submitted_addr and address and name_addr:
        loc = Nominatim(user_agent="bookmark_app").geocode(address)
        if loc:
            st.session_state.bookmarks.append({
                "name": name_addr.strip(),
                "coords": [loc.latitude, loc.longitude],
                "color": color_addr,
                "icon": icon_addr
            })
            st.success(f"추가됨: {name_addr} ({loc.latitude:.5f}, {loc.longitude:.5f})")
        else:
            st.error("주소를 찾을 수 없습니다.")

# 북마크 목록 + 초기화
if st.session_state.bookmarks:
    st.markdown("---")
    st.subheader("📚 북마크 목록")
    for idx, bm in enumerate(st.session_state.bookmarks, 1):
        st.write(f"{idx}. {bm['name']} — ({bm['coords'][0]:.4f}, {bm['coords'][1]:.4f}) | 색상: {bm['color']}, 아이콘: {bm['icon']}")
    if st.button("🔄 초기화"):
        st.session_state.bookmarks = []
        st.experimental_rerun()

else:
    st.info("북마크가 없습니다.")

# folium 지도 생성 및 위젯
m = folium.Map(location=default_location, zoom_start=12)
for bm in st.session_state.bookmarks:
    folium.Marker(
        location=bm["coords"],
        popup=bm["name"],
        icon=folium.Icon(color=bm["color"], icon=bm["icon"], prefix="fa")
    ).add_to(m)

map_data = st_folium(m, width=700, height=500)

# 지도 클릭폼은 map_data 표시 이후 아래쪽에
if map_data and map_data.get("last_clicked"):
    clicked = map_data["last_clicked"]
    with st.form("click_form"):
        st.success(f"📍 선택된 위치: {clicked}")
        name_click = st.text_input("북마크 이름", key="click_nm")
        color_click = st.selectbox("마커 색상", colors, key="click_color")
        icon_click = st.selectbox("아이콘", icons, key="click_icon")
        submitted_click = st.form_submit_button("클릭위치 추가")
        if submitted_click and name_click:
            st.session_state.bookmarks.append({
                "name": name_click.strip(),
                "coords": [clicked["lat"], clicked["lng"]],
                "color": color_click,
                "icon": icon_click
            })
            st.experimental_rerun()
