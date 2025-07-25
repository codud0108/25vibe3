import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

st.set_page_config(page_title="📍 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도")

if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []

geolocator = Nominatim(user_agent="bookmark_app")
colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightblue", "black"]
icons = ["info-sign", "home", "star", "flag", "cloud", "heart", "gift", "leaf"]

# 📥 폴더 목록 수집
folder_set = set([bm.get("folder", "기본") for bm in st.session_state.bookmarks])
selected_folder = st.selectbox("📂 폴더 선택", ["전체"] + sorted(folder_set))

# 📥 검색
query = st.text_input("🔍 북마크 이름 검색", placeholder="예: 스타벅스")

# 📥 주소 입력으로 북마크 추가
with st.form("addr_form"):
    st.subheader("🏠 주소로 북마크 추가")
    col1, col2 = st.columns(2)
    with col1:
        address = st.text_input("주소 입력")
        name = st.text_input("이름")
        folder = st.text_input("폴더 이름", value="기본")
    with col2:
        description = st.text_input("설명")
        color = st.selectbox("색상", colors)
        icon = st.selectbox("아이콘", icons)

    if st.form_submit_button("추가"):
        if address and name:
            loc = geolocator.geocode(address)
            if loc:
                st.session_state.bookmarks.append({
                    "name": name.strip(),
                    "coords": [loc.latitude, loc.longitude],
                    "address": loc.address,
                    "description": description.strip(),
                    "color": color,
                    "icon": icon,
                    "folder": folder.strip()
                })
                st.success("✅ 북마크 추가됨")
                st.experimental_rerun()
            else:
                st.error("❌ 주소를 찾을 수 없습니다.")

# 📍 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

# 📌 마커 추가 (drag enabled)
for idx, bm in enumerate(st.session_state.bookmarks):
    if selected_folder != "전체" and bm.get("folder") != selected_folder:
        continue
    if query and query.lower() not in bm["name"].lower():
        continue

    marker = folium.Marker(
        location=bm["coords"],
        popup=f"<b>{bm['name']}</b><br>{bm.get('address','')}<br>{bm.get('description','')}",
        draggable=True,
        icon=folium.Icon(color=bm["color"], icon=bm["icon"], prefix="fa")
    )
    marker.add_to(m)

    # JavaScript로 dragend 이벤트 처리
    marker.add_child(folium.Element(f"""
        <script>
        var marker = this;
        marker.on('dragend', function(e) {{
            var lat = e.target.getLatLng().lat;
            var lng = e.target.getLatLng().lng;
            fetch("/?drag_id={idx}&lat=" + lat + "&lng=" + lng);
        }});
        </script>
    """))

# 지도 출력
map_result = st_folium(m, width=700, height=500)

# 📌 지도 클릭 시 폼
if map_result and map_result.get("last_clicked"):
    clicked = map_result["last_clicked"]
    lat, lng = clicked["lat"], clicked["lng"]
    address = geolocator.reverse((lat, lng), language="ko")
    real_address = address.address if address else "주소 없음"

    with st.form("click_form"):
        st.subheader("🖱️ 클릭한 위치 추가")
        name = st.text_input("이름", key="click_name")
        folder = st.text_input("폴더", value="기본", key="click_folder")
        description = st.text_input("설명", key="click_desc")
        color = st.selectbox("색상", colors, key="click_color")
        icon = st.selectbox("아이콘", icons, key="click_icon")
        submit = st.form_submit_button("지도로 추가")
        if submit and name:
            st.session_state.bookmarks.append({
                "name": name.strip(),
                "coords": [lat, lng],
                "address": real_address,
                "description": description.strip(),
                "color": color,
                "icon": icon,
                "folder": folder.strip()
            })
            st.success("✅ 북마크 추가됨")
            st.experimental_rerun()

# 📋 북마크 목록
st.markdown("---")
st.subheader("📚 북마크 목록")

editable = [
    (i, bm) for i, bm in enumerate(st.session_state.bookmarks)
    if (selected_folder == "전체" or bm.get("folder") == selected_folder)
    and (query.lower() in bm["name"].lower())
]

for i, bm in editable:
    with st.expander(f"{bm['name']} ({bm.get('folder', '기본')})"):
        bm["name"] = st.text_input("이름", bm["name"], key=f"name_{i}")
        bm["description"] = st.text_input("설명", bm.get("description", ""), key=f"desc_{i}")
        bm["folder"] = st.text_input("폴더", bm.get("folder", "기본"), key=f"folder_{i}")
        bm["color"] = st.selectbox("색상", colors, index=colors.index(bm["color"]), key=f"color_{i}")
        bm["icon"] = st.selectbox("아이콘", icons, index=icons.index(bm["icon"]), key=f"icon_{i}")
        st.text(f"📍 좌표: {bm['coords'][0]:.5f}, {bm['coords'][1]:.5f}")
        st.text(f"🏠 주소: {bm.get('address', '없음')}")
        col1, col2 = st.columns(2)
        if col1.button("❌ 삭제", key=f"del_{i}"):
            st.session_state.bookmarks.pop(i)
            st.experimental_rerun()
        if col2.button("✅ 저장", key=f"save_{i}"):
            st.success("✔️ 수정 완료")

# 📁 다운로드 버튼
if st.session_state.bookmarks:
    df = pd.DataFrame(st.session_state.bookmarks)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 CSV로 저장", csv, "bookmarks.csv", "text/csv")

# 🔄 전체 초기화
if st.button("🧹 모든 북마크 초기화"):
    st.session_state.bookmarks = []
    st.experimental_rerun()
