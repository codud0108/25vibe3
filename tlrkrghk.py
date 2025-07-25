import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="서울 인구 피라미드", layout="wide")
st.title("👥 서울특별시 연령별 인구 피라미드 (2025년 6월 기준)")

# CSV 파일 업로드
uploaded_file = st.file_uploader("📂 연령별 인구 데이터 (CSV, euc-kr 인코딩)", type=["csv"])
if uploaded_file is not None:
    try:
        # 파일 읽기
        df = pd.read_csv(uploaded_file, encoding="euc-kr")

        # 서울시 전체 데이터 추출
        seoul_total = df[df["행정구역"].str.contains("서울특별시  \(1100000000\)")]

        # 남성과 여성 컬럼 추출
        male_cols = [col for col in df.columns if "남_" in col and "세" in col]
        female_cols = [col for col in df.columns if "여_" in col and "세" in col]
        ages = [col.split("_")[-1] for col in male_cols]

        # 인구 수 전처리: 쉼표 제거 → float → int
        male_counts = seoul_total[male_cols].iloc[0].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)
        female_counts = seoul_total[female_cols].iloc[0].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)

        # 인구 피라미드 그리기
        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=ages,
            x=-male_counts,
            name="남자",
            orientation="h",
            marker_color="blue"
        ))

        fig.add_trace(go.Bar(
            y=ages,
            x=female_counts,
            name="여자",
            orientation="h",
            marker_color="red"
        ))

        fig.update_layout(
            title="서울특별시 연령별 인구 피라미드 (2025년 6월)",
            barmode="relative",
            xaxis_title="인구수",
            yaxis_title="나이",
            xaxis_tickformat=",d",
            height=1000,
            yaxis=dict(autorange="reversed"),
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"파일을 처리하는 중 오류가 발생했습니다: {e}")
else:
    st.info("왼쪽 사이드바에서 CSV 파일을 업로드해주세요.")
