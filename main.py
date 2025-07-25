import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

# 기본 설정
st.set_page_config(page_title="📍 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도")

# 세션 초기화
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []
if "folder_colors" not in st.session_state:
    st.session_state.folder_colors = {}
if "map_center" not in st.session_state:
    st.session_state.map_center = [37.5665, 126.9780]  # 서울 기본

# 설정값
default_colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightblue", "black"]
icons = ["info-sign", "home", "star", "flag", "cloud", "heart", "gift", "leaf"]
geolocator = Nominatim(user_agent="bookmark_app")

# 필터 UI
all_folders = list(set(bm.get("folder", "기본") for bm in st.session_state.bookmarks))
selected_folder = st.selectbox("📂 폴더 필터", ["전체"] + sorted(all_folders))
query = st.text_input("🔍 북마크 검색 (이름 또는 설명)")
sort_option = st.selectbox("🔃 정렬 기준", ["이름순", "폴더순", "최신순"])

# 폴더별 색상 설정
st.markdown("### 🎨 폴더별 색상 설정")
for folder in sorted(all_folders):
    current_color = st.session_state.folder_colors.get(folder, "blue")
    st.session_state.folder_colors[folder] = st.selectbox(
        f"폴더: {folder}", default_colors,
        index=default_colors.index(current_color) if current_color in default_colors else 0,
        key=f"color_{folder}"
    )

# 북마크 추가 폼
with st.form("add_bookmark_form"):
    st.markdown("### ➕ 북마크 추가")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("이름")
        folder = st.text_input("폴더", value="기본")
        desc = st.text_input("설명")
    with col2:
        address = st.text_input("주소")
        icon = st.selectbox("아이콘", icons)

    if st.form_submit_button("추가") and name and address:
        loc = geolocator.geocode(address)
        if loc:
            color = st.session_state.folder_colors.get(folder, "blue")
            new_bookmark = {
                "name": name.strip(),
                "folder": folder.strip(),
                "description": desc.strip(),
                "address": loc.address,
                "coords": [loc.latitude, loc.longitude],
                "icon": icon,
                "color": color
            }
            st.session_state.bookmarks.append(new_bookmark)
            st.success(f"✅ '{name}' 북마크가 추가되었습니다.")

# 정렬 함수
def sort_bookmarks(data, method):
    if method == "이름순":
        return sorted(data, key=lambda x: x["name"])
    if method == "폴더순":
        return sorted(data, key=lambda x: (x["folder"], x["name"]))
    return list(reversed(data))  # 최신순

# 지도 생성 (중심: 최근 클릭 북마크 또는 기본)
map_center = st.session_state.map_center
m = folium.Map(location=map_center, zoom_start=16)
cluster = MarkerCluster().add_to(m)

# 정렬된 북마크 필터링 및 지도 마커 표시
sorted_bookmarks = sort_bookmarks(st.session_state.bookmarks, sort_option)
for bm in sorted_bookmarks:
    if selected_folder != "전체" and bm.get("folder") != selected_folder:
        continue
    if query and query.lower() not in bm["name"].lower() and query.lower() not in bm["description"].lower():
        continue

    folium.Marker(
        location=bm["coords"],
        popup=f"<b>{bm['name']}</b><br>{bm.get('folder')}<br>{bm.get('description')}<br>{bm.get('address')}",
        icon=folium.Icon(
            color=st.session_state.folder_colors.get(bm["folder"], "blue"),
            icon=bm["icon"], prefix="fa"
        )
    ).add_to(cluster)

# 지도 표시
st.markdown("### 🗺️ 북마크 지도")
st_folium(m, width=700, height=500)

# 북마크 목록 표시
st.markdown("### 📋 북마크 목록")
for i, bm in enumerate(sorted_bookmarks):
    if selected_folder != "전체" and bm.get("folder") != selected_folder:
        continue
    if query and query.lower() not in bm["name"].lower() and query.lower() not in bm["description"].lower():
        continue

    with st.expander(f"{bm['name']} ({bm['folder']})"):
        bm["name"] = st.text_input("이름", value=bm["name"], key=f"name_{i}")
        bm["description"] = st.text_input("설명", value=bm["description"], key=f"desc_{i}")
        bm["folder"] = st.text_input("폴더", value=bm["folder"], key=f"folder_{i}")
        bm["icon"] = st.selectbox("아이콘", icons, index=icons.index(bm["icon"]), key=f"icon_{i}")
        bm["color"] = st.session_state.folder_colors.get(bm["folder"], "blue")
        st.text(f"📍 좌표: {bm['coords'][0]:.5f}, {bm['coords'][1]:.5f}")
        st.text(f"🏠 주소: {bm.get('address','')}")

        col1, col2, col3 = st.columns(3)
        if col1.button("❌ 삭제", key=f"del_{i}"):
            del st.session_state.bookmarks[i]
            st.experimental_rerun()
        if col2.button("✅ 저장", key=f"save_{i}"):
            st.success("✔️ 수정 완료")
        if col3.button("📍 지도에서 보기", key=f"view_{i}"):
            st.session_state.map_center = bm["coords"]
            st.experimental_rerun()

# CSV 다운로드
if st.session_state.bookmarks:
    df = pd.DataFrame(st.session_state.bookmarks)
    st.download_button("📥 CSV 다운로드", df.to_csv(index=False), "bookmarks.csv", "text/csv")

# 전체 초기화
if st.button("🧹 전체 초기화"):
    st.session_state.bookmarks = []
    st.session_state.folder_colors = {}
    st.session_state.map_center = [37.5665, 126.9780]
    st.experimental_rerun()
