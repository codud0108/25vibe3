import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

st.set_page_config(page_title="📍 북마크 지도", layout="wide")
st.markdown("## 📍 나만의 북마크 지도")

# 초기화
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []
if "folder_colors" not in st.session_state:
    st.session_state.folder_colors = {}

geolocator = Nominatim(user_agent="bookmark_app")
default_location = [37.5665, 126.9780]
default_colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightblue", "black"]
icons = ["info-sign", "home", "star", "flag", "cloud", "heart", "gift", "leaf"]

# 폴더 목록
all_folders = list(set(bm.get("folder", "기본") for bm in st.session_state.bookmarks))
selected_folder = st.selectbox("📂 폴더 필터", ["전체"] + sorted(all_folders))
query = st.text_input("🔍 북마크 이름 검색", placeholder="예: 스타벅스")

# 📁 폴더 색상 설정 UI
st.markdown("### 🎨 폴더별 색상 설정")
for folder in sorted(all_folders):
    current_color = st.session_state.folder_colors.get(folder, "blue")
    st.session_state.folder_colors[folder] = st.selectbox(
        f"폴더: {folder}", default_colors,
        index=default_colors.index(current_color) if current_color in default_colors else 0,
        key=f"folder_color_{folder}"
    )

# 📥 북마크 추가 (주소 입력)
with st.form("add_bookmark_form"):
    st.markdown("### ➕ 북마크 추가")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("이름")
        folder = st.text_input("폴더", value="기본")
        description = st.text_input("설명")
    with col2:
        address = st.text_input("주소")
        icon = st.selectbox("아이콘", icons)
    submitted = st.form_submit_button("추가")

    if submitted and name and address:
        loc = geolocator.geocode(address)
        if loc:
            color = st.session_state.folder_colors.get(folder.strip(), "blue")
            st.session_state.bookmarks.append({
                "name": name.strip(),
                "folder": folder.strip(),
                "description": description.strip(),
                "address": loc.address,
                "coords": [loc.latitude, loc.longitude],
                "icon": icon,
                "color": color
            })
            st.success("✅ 북마크 추가됨")
            st.experimental_rerun()
        else:
            st.error("❌ 주소를 찾을 수 없습니다.")

# 🗺️ 지도 생성 with 마커 클러스터링
m = folium.Map(location=default_location, zoom_start=12)
marker_cluster = MarkerCluster().add_to(m)

for idx, bm in enumerate(st.session_state.bookmarks):
    if selected_folder != "전체" and bm.get("folder") != selected_folder:
        continue
    if query and query.lower() not in bm["name"].lower():
        continue

    folium.Marker(
        location=bm["coords"],
        popup=f"<b>{bm['name']}</b><br>{bm.get('folder','')}<br>{bm.get('description','')}<br>{bm.get('address','')}",
        icon=folium.Icon(color=st.session_state.folder_colors.get(bm["folder"], "blue"),
                         icon=bm.get("icon", "info-sign"), prefix="fa")
    ).add_to(marker_cluster)

# 지도 출력
st.markdown("### 🗺️ 북마크 지도")
st_folium(m, width=700, height=500)

# 📋 북마크 목록 (간격 최소화)
st.markdown("### 📚 북마크 목록")
results = [
    (i, bm) for i, bm in enumerate(st.session_state.bookmarks)
    if (selected_folder == "전체" or bm.get("folder") == selected_folder)
    and (query.lower() in bm["name"].lower())
]

for i, bm in results:
    with st.expander(f"📌 {bm['name']} ({bm.get('folder','기본')})", expanded=False):
        bm["name"] = st.text_input("이름", value=bm["name"], key=f"name_{i}")
        bm["description"] = st.text_input("설명", value=bm.get("description", ""), key=f"desc_{i}")
        bm["folder"] = st.text_input("폴더", value=bm.get("folder", "기본"), key=f"folder_{i}")
        bm["icon"] = st.selectbox("아이콘", icons, index=icons.index(bm["icon"]), key=f"icon_{i}")
        bm["color"] = st.session_state.folder_colors.get(bm["folder"], "blue")
        st.text(f"📍 좌표: {bm['coords'][0]:.5f}, {bm['coords'][1]:.5f}")
        st.text(f"🏠 주소: {bm.get('address','')}")

        col1, col2 = st.columns(2)
        if col1.button("❌ 삭제", key=f"del_{i}"):
            st.session_state.bookmarks.pop(i)
            st.experimental_rerun()
        if col2.button("✅ 저장", key=f"save_{i}"):
            st.success("✔️ 수정 완료")

# 📁 CSV 다운로드
if st.session_state.bookmarks:
    df = pd.DataFrame(st.session_state.bookmarks)
    st.download_button("📥 CSV 다운로드", df.to_csv(index=False), "bookmarks.csv", "text/csv")

# 전체 초기화
if st.button("🧹 전체 초기화"):
    st.session_state.bookmarks = []
    st.session_state.folder_colors = {}
    st.experimental_rerun()
