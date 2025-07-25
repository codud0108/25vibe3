import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="인구 피라미드 시각화", layout="wide")
st.title("👥 지역별 연령별 인구 피라미드 (2025년 6월 기준)")

# 파일 업로드
uploaded_file = st.file_uploader("📂 연령별 인구 데이터 (CSV, euc-kr 인코딩)", type=["csv"])

if uploaded_file is not None:
    try:
        # CSV 읽기
        df = pd.read_csv(uploaded_file, encoding="euc-kr")

        # ⬅️ 사이드바: 지역 선택
        st.sidebar.header("📍 지역 및 연령 설정")
        available_regions = df["행정구역"].dropna().unique()
        selected_region = st.sidebar.selectbox("지역을 선택하세요", options=available_regions)

        # 연령 컬럼 파악
        male_cols = [col for col in df.columns if "남_" in col and "세" in col]
        female_cols = [col for col in df.columns if "여_" in col and "세" in col]
        age_labels = [col.split("_")[-1].replace("세", "").replace(" ", "").replace("이상", "") for col in male_cols]

        # 정수로 변환 가능한 것만 필터 (100세 이상 제거용)
        valid_ages = [int(age) for age in age_labels if age.isdigit()]

        # 연령 슬라이더
        min_age, max_age = st.sidebar.slider("연령 범위 선택 (세)", min_value=min(valid_ages),
                                             max_value=max(valid_ages), value=(0, 100))

        # 해당 지역 데이터 선택
        selected_df = df[df["행정구역"] == selected_region]

        # 나이 범위에 맞는 컬럼만 필터링
        filtered_male_cols = [col for col in male_cols if min_age <= int(col.split("_")[-1].replace("세", "").replace("이상", "").strip()) <= max_age]
        filtered_female_cols = [col for col in female_cols if min_age <= int(col.split("_")[-1].replace("세", "").replace("이상", "").strip()) <= max_age]
        filtered_ages = [col.split("_")[-1] for col in filtered_male_cols]

        # 값 전처리
        male_counts = selected_df[filtered_male_cols].iloc[0].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)
        female_counts = selected_df[filtered_female_cols].iloc[0].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)

        # 인구 피라미드
        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=filtered_ages,
            x=-male_counts,
            name="남자",
            orientation="h",
            marker_color="blue"
        ))

        fig.add_trace(go.Bar(
            y=filtered_ages,
            x=female_counts,
            name="여자",
            orientation="h",
            marker_color="red"
        ))

        fig.update_layout(
            title=f"{selected_region} 인구 피라미드 (2025년 6월) - 연령 {min_age}세 ~ {max_age}세",
            barmode="relative",
            xaxis_title="인구수",
            yaxis_title="나이",
            xaxis_tickformat=",d",
            height=1000,
            yaxis=dict(autorange="reversed"),
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
else:
    st.info("왼쪽에서 CSV 파일을 업로드해주세요.")
