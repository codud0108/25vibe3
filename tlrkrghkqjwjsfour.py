import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="📊 법정동별 인구 증감 시각화", layout="wide")
st.title("📊 2025년 6월 법정동별 인구 증감 시각화")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요 (euc-kr 인코딩)", type="csv")

if uploaded_file:
    # CSV 읽기
    try:
        df = pd.read_csv(uploaded_file, encoding="euc-kr")
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding="utf-8")

    # 숫자형으로 변환 (콤마 제거)
    df["증감"] = df["2025년06월_인구증감_계"].astype(str).str.replace(",", "").astype(int)

    # 가장 큰 변화 상위 30개 지역만 추출
    df_sorted = df.sort_values(by="증감", ascending=False)
    top_n = st.slider("표시할 지역 수", 10, 100, 30)
    df_display = pd.concat([df_sorted.head(top_n // 2), df_sorted.tail(top_n // 2)])

    # 막대그래프
    fig = px.bar(
        df_display,
        x="법정구역",
        y="증감",
        color="증감",
        color_continuous_scale="RdBu",
        title="📈 지역별 인구 증감 (상위 및 하위)",
        labels={"증감": "인구 증감 수", "법정구역": "지역"},
    )

    fig.update_layout(xaxis_tickangle=-45, height=600)

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("좌측 사이드바에서 CSV 파일을 업로드하면 시각화가 나타납니다.")
