import streamlit as st
from streamlit_folium import st_folium
import folium

# 페이지 기본 설정
st.set_page_config(page_title="나만의 북마크 지도", layout="wide")
st.title("📍 나만의 북마크 지도")
st.caption("지도에서 원하는 위치를 클릭하고 북마크를 추가해보세요!")

# 세션 상태 초기화
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = []

# 기본 위치 (서울 중심)
default_location = [37.5665, 126.9780]

# folium 지도 생성
m = folium.Map(location=default_location, zoom_start=12)

# 기존 북마크를 지도에 마커로 표시
for bm in st.session_state.bookmarks:
    folium.Marker(location=bm["coords"], popup=bm["name"], icon=folium.Icon(color="blue")).add_to(m)

# 지도에 클릭 기능 추가
click_info = st_folium(m, width=700, height=500)

# 사용자가 지도를 클릭했을 때
if click_info and click_info["last_clicked"]:
    clicked_coords = click_info["last_clicked"]
    st.success(f"선택된 위치: {clicked_coords}")

    with st.form("bookmark_form"):
        name = st.text_input("📝 북마크 이름", "")
        submitted = st.form_submit_button("북마크 추가")

        if submitted and name.strip():
            # 북마크 저장
            st.session_state.bookmarks.append({
                "name": name.strip(),
                "coords": [clicked_coords["lat"], clicked_coords["lng"]]
            })
            st.experimental_rerun()

# 북마크 목록 표시
if st.session_state.bookmarks:
    st.markdown("### 📌 북마크 목록")
    for i, bm in enumerate(st.session_state.bookmarks, 1):
        st.write(f"{i}. {bm['name']} - ({bm['coords'][0]:.4f}, {bm['coords'][1]:.4f})")

    # 초기화 버튼
    if st.button("🔄 북마크 초기화"):
        st.session_state.bookmarks = []
        st.experimental_rerun()
