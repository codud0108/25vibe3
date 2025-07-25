
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="📍 나만의 북마크 지도", layout="wide")
st.title("🔐 북마크 지도 로그인")

# 사용자 세션 초기화
if "users" not in st.session_state:
    st.session_state.users = {}

# 로그인 입력
username = st.text_input("이름", key="login_name")
password = st.text_input("비밀번호", type="password", key="login_pwd")

# 로그인 처리
if st.button("로그인 / 회원가입"):
    if username and password:
        if username not in st.session_state.users:
            st.session_state.users[username] = {
                "password": password,
                "bookmarks": [],
                "folder_colors": {},
                "map_center": [37.5665, 126.9780],
            }
        elif st.session_state.users[username]["password"] != password:
            st.error("❌ 비밀번호가 틀렸습니다.")
            st.stop()
        st.session_state.current_user = username
        st.session_state.map_center = st.session_state.users[username]["map_center"]
    else:
        st.warning("이름과 비밀번호를 모두 입력하세요.")
        st.stop()

# 로그인 이후만 실행
if "current_user" in st.session_state:
    user = st.session_state.users[st.session_state.current_user]
    default_colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightblue", "black"]
    icons = ["info-sign", "home", "star", "flag", "cloud", "heart", "gift", "leaf"]
    geolocator = Nominatim(user_agent="bookmark_app")

    # 📍 북마크 추가
    st.markdown("## 📍 북마크 추가 및 지도")
    with st.form("add_bookmark_form"):
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
                color = user["folder_colors"].get(folder, "blue")
                user["bookmarks"].append({
                    "name": name.strip(),
                    "folder": folder.strip(),
                    "description": desc.strip(),
                    "address": loc.address,
                    "coords": [loc.latitude, loc.longitude],
                    "icon": icon,
                    "color": color
                })
                st.success("✅ 북마크 추가됨")

    # 지도 중심 위치
    map_center = st.session_state.get("map_center", user.get("map_center", [37.5665, 126.9780]))
    m = folium.Map(location=map_center, zoom_start=16)
    cluster = MarkerCluster().add_to(m)

    # 클릭 이벤트를 위한 숨겨진 상태값
    if "clicked_location" not in st.session_state:
        st.session_state.clicked_location = None

    # 마커 표시
    def sort_bookmarks(data, method):
        if method == "이름순":
            return sorted(data, key=lambda x: x["name"])
        if method == "폴더순":
            return sorted(data, key=lambda x: (x["folder"], x["name"]))
        return list(reversed(data))

    all_folders = list(set(bm.get("folder", "기본") for bm in user["bookmarks"]))
    selected_folder = st.selectbox("📂 폴더 필터", ["전체"] + sorted(all_folders))
    query = st.text_input("🔍 북마크 검색 (이름 또는 설명)")
    sort_option = st.selectbox("🔃 정렬 기준", ["이름순", "폴더순", "최신순"])

    sorted_bookmarks = sort_bookmarks(user["bookmarks"], sort_option)
    for bm in sorted_bookmarks:
        if selected_folder != "전체" and bm.get("folder") != selected_folder:
            continue
        if query and query.lower() not in bm["name"].lower() and query.lower() not in bm["description"].lower():
            continue
        folium.Marker(
            location=bm["coords"],
            popup=f"<b>{bm['name']}</b><br>{bm.get('folder')}<br>{bm.get('description')}<br>{bm.get('address')}",
            icon=folium.Icon(
                color=user["folder_colors"].get(bm["folder"], "blue"),
                icon=bm["icon"], prefix="fa"
            )
        ).add_to(cluster)

    # 지도 클릭 이벤트 처리용 JavaScript
    m.add_child(folium.LatLngPopup())
    folium.Marker(location=map_center, popup="중심 위치").add_to(m)

    result = st_folium(m, width=700, height=500)

    if result and result.get("last_clicked"):
        latlng = result["last_clicked"]
        st.session_state.clicked_location = latlng
        st.success(f"🆕 클릭된 위치: {latlng['lat']:.5f}, {latlng['lng']:.5f}")
        with st.form("map_click_form"):
            name = st.text_input("이름 (지도 클릭 추가)", key="click_name")
            folder = st.text_input("폴더", value="기본", key="click_folder")
            desc = st.text_input("설명", key="click_desc")
            icon = st.selectbox("아이콘", icons, key="click_icon")
            if st.form_submit_button("지도 위치로 추가"):
                user["bookmarks"].append({
                    "name": name.strip(),
                    "folder": folder.strip(),
                    "description": desc.strip(),
                    "address": "(지도 클릭 입력)",
                    "coords": [latlng["lat"], latlng["lng"]],
                    "icon": icon,
                    "color": user["folder_colors"].get(folder, "blue")
                })
                st.success("✅ 지도에서 북마크 추가됨")
                st.rerun()

    # 🎨 폴더 색상 설정
    st.markdown("## 🎨 폴더별 색상 설정")
    for folder in sorted(all_folders):
        current_color = user["folder_colors"].get(folder, "blue")
        user["folder_colors"][folder] = st.selectbox(
            f"폴더: {folder}", default_colors,
            index=default_colors.index(current_color) if current_color in default_colors else 0,
            key=f"color_{folder}"
        )

    # 📋 북마크 목록
    st.markdown("## 📋 북마크 목록")
    for i, bm in enumerate(sorted_bookmarks):
        if selected_folder != "전체" and bm.get("folder") != selected_folder:
            continue
        if query and query.lower() not in bm["name"].lower() and query.lower() not in bm["description"].lower():
            continue
        with st.expander(f"{bm['name']} ({bm['folder']})"):
            bm["name"] = st.text_input("이름", bm["name"], key=f"name_{i}")
            bm["description"] = st.text_input("설명", bm["description"], key=f"desc_{i}")
            bm["folder"] = st.text_input("폴더", bm["folder"], key=f"folder_{i}")
            bm["icon"] = st.selectbox("아이콘", icons, index=icons.index(bm["icon"]), key=f"icon_{i}")
            bm["color"] = user["folder_colors"].get(bm["folder"], "blue")
            st.text(f"📍 좌표: {bm['coords'][0]:.5f}, {bm['coords'][1]:.5f}")
            st.text(f"🏠 주소: {bm.get('address','')}")

            col1, col2, col3 = st.columns(3)
            if col1.button("❌ 삭제", key=f"del_{i}"):
                del user["bookmarks"][i]
                st.rerun()
            if col2.button("✅ 저장", key=f"save_{i}"):
                st.success("✔️ 수정 완료")
            if col3.button("📍 지도에서 보기", key=f"view_{i}"):
                user["map_center"] = bm["coords"]
                st.session_state.map_center = bm["coords"]
                st.rerun()

    # 📥 CSV 다운로드
    if user["bookmarks"]:
        df = pd.DataFrame(user["bookmarks"])
        st.download_button("📥 CSV 다운로드", df.to_csv(index=False), "bookmarks.csv", "text/csv")

    # 전체 초기화
    if st.button("🧹 전체 초기화"):
        user["bookmarks"] = []
        user["folder_colors"] = {}
        user["map_center"] = [37.5665, 126.9780]
        st.session_state.map_center = [37.5665, 126.9780]
        st.rerun() 
