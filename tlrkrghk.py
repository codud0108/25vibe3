import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 페이지 설정
st.set_page_config(page_title="연령 그룹별 인구 피라미드", layout="wide")
st.title("👥 시 단위 연령 그룹별 인구 피라미드 (2025년 6월 기준)")

# 파일 업로드
uploaded_file = st.file_uploader("📂 연령별 인구 데이터 (CSV, euc-kr 인코딩)", type=["csv"])

if uploaded_file is not None:
    try:
        # CSV 로드
        df = pd.read_csv(uploaded_file, encoding="euc-kr")

        # ✅ 시 단위만 필터링 (예: '서울특별시  (1100000000)' 형태)
        si_df = df[df["행정구역"].str.contains(r"\([0-9]{10}\)") & ~df["행정구역"].str.contains(r"[가-힣]+\(.+\)")]
        si_names = si_df["행정구역"].unique()

        # ⬅️ 사이드바: 시 선택
        st.sidebar.header("📍 시 단위 지역 및 연령 그룹 선택")
        selected_si = st.sidebar.selectbox("시 단위 지역을 선택하세요", options=si_names)

        # 연령 그룹 설정 (10세 단위)
        age_groups = [(f"{i}~{i+9}세", list(range(i, i+10))) for i in range(0, 100, 10)]
        age_groups.append(("100세 이상", list(range(100, 101))))  # 마지막 그룹

        group_names = [g[0] for g in age_groups]
        selected_groups = st.sidebar.multiselect("연령 그룹을 선택하세요", options=group_names, default=group_names)

        # 선택된 데이터 추출
        selected_row = df[df["행정구역"] == selected_si]

        # 성별 컬럼
        male_cols = [col for col in df.columns if "남_" in col and "세" in col]
        female_cols = [col for col in df.columns if "여_" in col and "세" in col]

        # 연령 숫자만 추출
        def extract_age(col_name):
            match = re.search(r"(\d+)세", col_name)
            return int(match.group(1)) if match else 100

        age_mapping = {col: extract_age(col) for col in male_cols}

        # 선택된 연령 컬럼 필터링
        selected_male_cols, selected_female_cols, selected_labels = [], [], []

        for group_name in selected_groups:
            group_range = dict(age_groups)[group_name]
            for col, age in age_mapping.items():
                if age in group_range:
                    selected_male_cols.append(col)
                    female_col = col.replace("남_", "여_")
                    if female_col in female_cols:
                        selected_female_cols.append(female_col)
                        selected_labels.append(col.split("_")[-1])  # 예: "20세"

        # 값 처리
        male_counts = selected_row[selected_male_cols].iloc[0].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)
        female_counts = selected_row[selected_female_cols].iloc[0].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)

        # Plotly 시각화
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=selected_labels,
            x=-male_counts,
            name="남자",
            orientation="h",
            marker_color="blue"
        ))
        fig.add_trace(go.Bar(
            y=selected_labels,
            x=female_counts,
            name="여자",
            orientation="h",
            marker_color="red"
        ))

        fig.update_layout(
            title=f"{selected_si} 인구 피라미드 - 선택한 연령 그룹",
            barmode="relative",
            xaxis_title="인구수",
            yaxis_title="연령",
            xaxis_tickformat=",d",
            height=1000,
            yaxis=dict(autorange="reversed"),
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
else:
    st.info("CSV 파일을 업로드해주세요.")
