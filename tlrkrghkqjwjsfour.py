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

    # 콤마 제거 후 숫자로 변환
    df["증감"] = df["2025년06월_인구증감_계"].astype(str).str.replace(",", "").astype(int)

    # 법정구역 컬럼에서 도, 시, 구 분리 (정규표현식 활용)
    df["도"] = df["법정구역"].str.extract(r"^([가-힣]+[도시특별시광역시자치시특별자치도]+)")
    df["시"] = df["법정구역"].str.extract(r"^.+? ([가-힣]+[시군구])")
    df["구"] = df["법정구역"].str.extract(r"^.+? .+? ([가-힣]+동|[가-힣]+면|[가-힣]+리)?")

    # 사이드바 필터
    st.sidebar.header("🔍 지역 선택")

    selected_do = st.sidebar.selectbox("도 선택", sorted(df["도"].dropna().unique()))
    filtered_df = df[df["도"] == selected_do]

    selected_si = st.sidebar.selectbox("시 선택", sorted(filtered_df["시"].dropna().unique()))
    filtered_df = filtered_df[filtered_df["시"] == selected_si]

    available_gu = filtered_df["구"].dropna().unique()
    if len(available_gu) > 0:
        selected_gu = st.sidebar.selectbox("구/동 선택", ["전체"] + sorted(available_gu))
        if selected_gu != "전체":
            filtered_df = filtered_df[filtered_df["구"] == selected_gu]

    # 정렬 후 시각화할 행 선택
    df_sorted = filtered_df.sort_values(by="증감", ascending=False)
    top_n = st.slider("표시할 지역 수", 10, 100, 30)
    df_display = pd.concat([df_sorted.head(top_n // 2), df_sorted.tail(top_n // 2)])

    # Plotly 그래프
    fig = px.bar(
        df_display,
        x="법정구역",
        y="증감",
        color="증감",
        color_continuous_scale="RdBu",
        title="📈 선택한 지역의 인구 증감",
        labels={"증감": "인구 증감 수", "법정구역": "지역"},
    )

    fig.update_layout(xaxis_tickangle=-45, height=600)

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📁 좌측 사이드바에서 CSV 파일을 업로드해주세요.")
