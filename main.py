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

    add_clicked = st.form_submit_button("추가")
    if add_clicked and name and address:
        loc = geolocator.geocode(address)
        if loc:
            color = st.session_state.folder_colors.get(folder, "blue")
            new_entry = {
                "name": name.strip(),
                "folder": folder.strip(),
                "description": desc.strip(),
                "address": loc.address,
                "coords": [loc.latitude, loc.longitude],
                "icon": icon,
                "color": color
            }
            if new_entry not in st.session_state.bookmarks:
                st.session_state.bookmarks.append(new_entry)
                st.success(f"✅ '{name}' 북마크 추가됨")
            else:
                st.warning("⚠️ 이미 동일한 북마크가 존재합니다.")
        else:
            st.error("❌ 주소를 찾을 수 없습니다.")
