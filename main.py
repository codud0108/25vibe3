import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# 설정
st.set_page_config(page_title="📍 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도")
st.caption("주소 또는 지도를 클릭해 북마크를 추가하고, 장소 설명도 함께 남겨보세요!")

# 초기화
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []

# 옵션
default_location = [37.5665, 126.9780]
colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightblue", "black"]
icons = ["info-sign", "home", "star", "flag", "cloud", "heart", "gift", "leaf"]

# 주소로 북마크 추가 폼
with st.form("address_form"):
    st.subheader("🏠 주소로 북마크 추가")
    address = st.text_input("주소 입력", key="addr_input")
    name = st.text_input("📌 북마크 이름", key="addr_name")
    description = st.text_input("📝 장소 설명", key="addr_desc")
    color = st.selectbox("🎨 색상", colors, key="addr_color")
    icon = st.selectbox("🔰 아이콘", icons, key="addr_icon")
    submit = st.form_submit_button("추가하기")
    if submit and address and name:
        geolocator = Nominatim(user_agent="bookmark_app")
        location = geolocator.geocode(address)
        if location:
            st.session_state.bookmarks.append({
                "name": name.strip(),
                "coords": [location.latitude, location.longitude],
                "address": location.address,
                "description": description.strip(),
                "color": color,
                "icon": icon
            })
            st.success(f"✅ '{name}' 추가됨")
            st.experimental_rerun()
        else:
            st.error("❌ 주소를 찾을 수 없습니다.")

# 북마크 목록
if st.session_state.bookmarks:
    st.markdown("---")
    st.subheader("📚 북마크 목록")
    for i, bm in enumerate(st.session_state.bookmarks, 1):
        st.write(f"""
        {i}. **{bm['name']}**
        - 🗺️ 위도/경도: ({bm['coords'][0]:.5f}, {bm['coords'][1]:.5f})
        - 🏠 주소: {bm.get('address', '주소 없음')}
        - 📝 설명: {bm.get('description', '설명 없음')}
        - 🎨 색상: {bm['color']}, 아이콘: {bm['icon']}
        """)
    if st.button("🔄 전체 초기화"):
        st.session_state.bookmarks = []
        st.experimental_rerun()
else:
    st.info("북마크가 없습니다.")

# 지도 생성
m = folium.Map(location=default_location, zoom_start=12)
for bm in st.session_state.bookmarks:
    popup_content = f"<b>{bm['name']}</b><br>{bm.get('address', '')}<br>{bm.get('description', '')}"
    folium.Marker(
        location=bm["coords"],
        popup=popup_content,
        icon=folium.Icon(color=bm["color"], icon=bm["icon"], prefix="fa")
    ).add_to(m)

# 지도 출력
map_data = st_folium(m, width=700, height=500)

# 지도 클릭 시 위치 정보 → 주소 변환 + 폼 표시
if map_data and map_data.get("last_clicked"):
    clicked = map_data["last_clicked"]
    lat, lng = clicked["lat"], clicked["lng"]
    geolocator = Nominatim(user_agent="bookmark_app")
    location = geolocator.reverse((lat, lng), language="ko")
    address = location.address if location else "주소를 찾을 수 없습니다."

    st.markdown("---")
    st.subheader("🖱️ 지도에서 선택한 위치")
    st.info(f"📍 위치: ({lat:.5f}, {lng:.5f})\n\n🏠 주소: {address}")

    with st.form("click_form"):
        name = st.text_input("📌 북마크 이름", key="click_name")
        description = st.text_input("📝 장소 설명", key="click_desc")
        color = st.selectbox("🎨 색상", colors, key="click_color")
        icon = st.selectbox("🔰 아이콘", icons, key="click_icon")
        submit = st.form_submit_button("지도로 추가")
        if submit and name:
            st.session_state.bookmarks.append({
                "name": name.strip(),
                "coords": [lat, lng],
                "address": address,
                "description": description.strip(),
                "color": color,
                "icon": icon
            })
            st.success(f"✅ '{name}' 추가됨")
            st.experimental_rerun()
