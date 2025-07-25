
import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="📊 평균연령 시각화", layout="wide")
st.title("📊 2025년 6월 지역별 평균연령 (남녀 비교)")

uploaded_file = st.file_uploader("📂 CSV 파일 업로드 (euc-kr 인코딩)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding="cp949")

        # 도, 시, 구(면읍동) 분리
        df["도"] = df["행정구역"].str.extract(r"^([가-힣]+[도시특별시광역시자치시특별자치도]+)")
        df["시"] = df["행정구역"].str.extract(r"^.+? ([가-힣]+[시군구])")
        df["구"] = df["행정구역"].str.extract(r"^.+? [가-힣]+[시군구] ([가-힣0-9]+)")[0]
        df["행정구역명"] = df["행정구역"].str.replace(r"\s*\(.*\)", "", regex=True)

        # 평균연령 숫자형 변환
        df["남자 평균연령"] = pd.to_numeric(df["2025년06월_남자 평균연령"], errors="coerce")
        df["여자 평균연령"] = pd.to_numeric(df["2025년06월_여자 평균연령"], errors="coerce")

        # 1. 도 선택
        selected_do = st.selectbox("📍 도 선택", sorted(df["도"].dropna().unique()))

        # 2. 시 선택
        filtered_si = df[df["도"] == selected_do]["시"].dropna().unique()
        selected_si = st.selectbox("🏙️ 시/군/구 선택", sorted(filtered_si))

        # 3. 구 선택 (선택적으로)
        filtered_gu = df[(df["도"] == selected_do) & (df["시"] == selected_si)]["구"].dropna().unique()
        selected_gu = st.selectbox("🏘️ 구/동/면 선택 (선택)", ["전체"] + sorted(filtered_gu))

        # 필터링
        if selected_gu == "전체":
            df_selected = df[(df["도"] == selected_do) & (df["시"] == selected_si)]
        else:
            df_selected = df[(df["도"] == selected_do) & (df["시"] == selected_si) & (df["구"] == selected_gu)]

        if df_selected.empty:
            st.warning("선택한 지역에 해당하는 데이터가 없습니다.")
        else:
            # Melt for Plotly
            df_melted = df_selected.melt(
                id_vars="행정구역명",
                value_vars=["남자 평균연령", "여자 평균연령"],
                var_name="성별", value_name="평균연령"
            )

            fig = px.bar(
                df_melted,
                x="행정구역명",
                y="평균연령",
                color="성별",
                barmode="group",
                title=f"{selected_do} {selected_si} {'' if selected_gu == '전체' else selected_gu} 평균 연령 비교",
                labels={"행정구역명": "지역", "평균연령": "평균 연령 (세)"}
            )
            fig.update_layout(xaxis_tickangle=-45, height=600)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
else:
    st.info("좌측 사이드바 또는 위에서 CSV 파일을 업로드해주세요.")
