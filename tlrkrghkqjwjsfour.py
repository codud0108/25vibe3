import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 페이지 설정
st.set_page_config(page_title="📊 법정동별 인구 증감 시각화", layout="wide")
st.title("📊 2025년 6월 법정동별 인구 증감 시각화")

# 파일 업로드
uploaded_file = st.file_uploader("📂 CSV 파일을 업로드하세요 (euc-kr 인코딩)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="euc-kr")
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding="utf-8")

    # 콤마 제거 후 숫자형 변환
    df["증감_계"] = df["2025년06월_인구증감_계"].astype(str).str.replace(",", "").astype(int)
    df["증감_남"] = df["2025년06월_인구증감_남자인구수"].astype(str).str.replace(",", "").astype(int)
    df["증감_여"] = df["2025년06월_인구증감_여자인구수"].astype(str).str.replace(",", "").astype(int)

    # 도/시/구 분리
    df["도"] = df["법정구역"].str.extract(r"^([가-힣]+[도시특별시광역시자치시특별자치도]+)")
    df["시"] = df["법정구역"].str.extract(r"^.+? ([가-힣]+[시군구])")
    df["구"] = df["법정구역"].str.extract(r"^.+? .+? ([가-힣]+동|[가-힣]+면|[가-힣]+리)?")

    # 사이드바 필터링
    st.sidebar.header("🔍 지역 선택")

    selected_dos = st.sidebar.multiselect("도 선택", sorted(df["도"].dropna().unique()))
    filtered_df = df[df["도"].isin(selected_dos)] if selected_dos else df.copy()

    selected_sis = st.sidebar.multiselect("시 선택", sorted(filtered_df["시"].dropna().unique()))
    filtered_df = filtered_df[filtered_df["시"].isin(selected_sis)] if selected_sis else filtered_df

    gu_options = sorted(filtered_df["구"].dropna().unique())
    selected_gus = st.sidebar.multiselect("구/동 선택", ["전체"] + gu_options)
    if selected_gus and "전체" not in selected_gus:
        filtered_df = filtered_df[filtered_df["구"].isin(selected_gus)]

    # 성별 선택
    st.sidebar.header("👥 성별 선택")
    gender_option = st.sidebar.radio("시각화할 인구 증감 항목을 선택하세요:", ["전체", "남자", "여자"])

    # 필터링 결과 확인
    if filtered_df.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
        st.stop()

    # 성별에 따른 y값 설정
    if gender_option == "전체":
        y_column = "증감_계"
        title = "📈 전체 인구 증감"
    elif gender_option == "남자":
        y_column = "증감_남"
        title = "📈 남자 인구 증감"
    else:
        y_column = "증감_여"
        title = "📈 여자 인구 증감"

    # Plotly 막대그래프
    fig = px.bar(
        filtered_df,
        x="법정구역",
        y=y_column,
        color=y_column,
        color_continuous_scale="RdBu",
        title=title,
        labels={y_column: "인구 증감 수", "법정구역": "지역"},
    )

    fig.update_layout(xaxis_tickangle=-45, height=700)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📁 좌측 사이드바에서 CSV 파일을 업로드해주세요.")
