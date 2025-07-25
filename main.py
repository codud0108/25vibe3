import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd
import io

st.set_page_config(page_title="📍 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도")

# 초기화
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []

# 기본값
default_location = [37.5665, 126.9780]
colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightblue", "black"]
icons = ["info-sign", "home", "star", "flag", "cloud", "heart", "gift", "leaf"]

geolocator = Nominatim(user_agent="bookmark_app")

# 📁 CSV 저장 기능
def download_csv():
    df = pd.DataFrame(st.session_state.bookmarks)
    csv = df.to_csv(index=False)
    st.download_button(
        label="📁 북마크 CSV 다운로드",
        data=csv,
        file_name="bookmarks.csv",
        mime="text/csv"
    )

# 🔍 북마크 검색 기능
st.subheader("🔍 북마크 검색")
query = st.text_input("이름으로 검색", placeholder="예: 스타벅스")

# 📥 북마크 추가 (주소 입력)
with st.form("addr_form"):
    st.subheader("🏠 주소로 북마크 추가")
    address = st.text_input("주소")
    name = st.text_input("이름")
    desc = st.text_input("설명")
    color = st.selectbox("색상", colors)
    icon = st.selectbox("아이콘", icons)
    submit = st.form_submit_button("주소로 추가")
    if submit and address and name:
        loc = geolocator.geocode(address)
        if loc:
            st.session_state.bookmarks.append({
                "name": name.strip(),
                "coords": [loc.latitude, loc.longitude],
                "address": loc.address,
                "description": desc.strip(),
                "color": color,
                "icon": icon
            })
            st.success("✅ 북마크 추가됨")
            st.experimental_rerun()
        else:
            st.error("❌ 주소를 찾을 수 없습니다.")

# 🗺️ 지도 생성
m = folium.Map(location=default_location, zoom_start=12)
for bm in st.session_state.bookmarks:
    folium.Marker(
        location=bm["coords"],
        popup=f"<b>{bm['name']}</b><br>{bm.get('address', '')}<br>{bm.get('description', '')}",
        icon=folium.Icon(color=bm["color"], icon=bm["icon"], prefix="fa")
    ).add_to(m)

# 📍 지도 출력
map_data = st_folium(m, width=700, height=500)

# 📍 지도 클릭 → 북마크 추가
if map_data and map_data.get("last_clicked"):
    clicked = map_data["last_clicked"]
    lat, lng = clicked["lat"], clicked["lng"]
    location = geolocator.reverse((lat, lng), language="ko")
    rev_addr = location.address if location else "주소를 찾을 수 없음"

    st.markdown("---")
    st.subheader("🖱️ 지도에서 선택된 위치")
    st.info(f"위치: ({lat:.5f}, {lng:.5f})\n\n주소: {rev_addr}")

    with st.form("click_form"):
        name = st.text_input("이름", key="click_name")
        desc = st.text_input("설명", key="click_desc")
        color = st.selectbox("색상", colors, key="click_color")
        icon = st.selectbox("아이콘", icons, key="click_icon")
        submitted = st.form_submit_button("지도로 추가")
        if submitted and name:
            st.session_state.bookmarks.append({
                "name": name.strip(),
                "coords": [lat, lng],
                "address": rev_addr,
                "description": desc.strip(),
                "color": color,
                "icon": icon
            })
            st.success("✅ 북마크 추가됨")
            st.experimental_rerun()

# 📋 북마크 목록 + 검색 + 수정
st.markdown("---")
st.subheader("📚 북마크 목록 및 수정")

filtered = [
    bm for bm in st.session_state.bookmarks
    if query.lower() in bm["name"].lower()
]

if filtered:
    for i, bm in enumerate(filtered):
        with st.expander(f"{i+1}. {bm['name']}"):
            bm["name"] = st.text_input("📝 이름", value=bm["name"], key=f"name_{i}")
            bm["description"] = st.text_input("📄 설명", value=bm.get("description", ""), key=f"desc_{i}")
            bm["color"] = st.selectbox("🎨 색상", colors, index=colors.index(bm["color"]), key=f"color_{i}")
            bm["icon"] = st.selectbox("🔰 아이콘", icons, index=icons.index(bm["icon"]), key=f"icon_{i}")
            st.markdown(f"📍 위치: {bm['coords'][0]:.5f}, {bm['coords'][1]:.5f}")
            st.markdown(f"🏠 주소: {bm.get('address', '없음')}")

            col1, col2 = st.columns(2)
            if col1.button("❌ 삭제", key=f"del_{i}"):
                st.session_state.bookmarks.remove(bm)
                st.experimental_rerun()
            if col2.button("✅ 저장", key=f"save_{i}"):
                st.success("✔️ 수정 완료")
else:
    st.warning("검색 결과가 없습니다.")

# 📁 CSV 저장 버튼
st.markdown("---")
download_csv()

# 🔄 전체 초기화
if st.button("🧹 전체 초기화"):
    st.session_state.bookmarks = []
    st.experimental_rerun()
