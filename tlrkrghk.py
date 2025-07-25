import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 페이지 설정
st.set_page_config(page_title="다중 지역 인구 피라미드", layout="wide")
st.title("👥 도-시-구 다중 선택 인구 피라미드 비교 (2025년 6월 기준)")

# CSV 업로드
uploaded_file = st.file_uploader("📂 연령별 인구 데이터 (CSV, euc-kr 인코딩)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding="euc-kr")

        # 도/시/구 분리
        df = df.copy()
        df["도"] = df["행정구역"].str.extract(r"^([가-힣]+[도|시|특별시|광역시|자치시|자치도|특별자치도])")
        df["시"] = df["행정구역"].str.extract(r"^.+? ([가-힣]+[시|군|구])")
        df["구"] = df["행정구역"].str.extract(r".+? ([가-힣]+동|[가-힣]+구|[가-힣]+면|[가-힣]+읍)")

        # 지역 식별용 라벨 생성
        df["지역"] = df[["도", "시", "구"]].fillna("").agg(" ".join, axis=1).str.strip()

        # 연령 그룹 설정
        st.sidebar.header("🎚️ 연령 그룹 선택")
        age_groups = [(f"{i}~{i+9}세", list(range(i, i+10))) for i in range(0, 100, 10)]
        age_groups.append(("100세 이상", list(range(100, 101))))
        group_names = [g[0] for g in age_groups]
        selected_groups = st.sidebar.multiselect("연령 그룹 선택", group_names, default=group_names)

        # 지역 선택
        st.sidebar.header("📍 비교할 지역 선택")
        available_regions = df["지역"].dropna().unique()
        selected_regions = st.sidebar.multiselect("여러 지역 선택", options=sorted(available_regions), default=sorted(available_regions)[:3])

        if not selected_regions:
            st.warning("최소 한 개 이상의 지역을 선택하세요.")
            st.stop()

        # 연령 컬럼 정리
        male_cols = [col for col in df.columns if "남_" in col and "세" in col]
        female_cols = [col for col in df.columns if "여_" in col and "세" in col]

        def extract_age(col_name):
            match = re.search(r"(\d+)세", col_name)
            return int(match.group(1)) if match else 100

        age_mapping = {col: extract_age(col) for col in male_cols}

        # 선택 연령 그룹 컬럼
        selected_male_cols, selected_female_cols, selected_labels = [], [], []
        for group_name in selected_groups:
            group_range = dict(age_groups)[group_name]
            for col, age in age_mapping.items():
                if age in group_range:
                    selected_male_cols.append(col)
                    female_col = col.replace("남_", "여_")
                    if female_col in female_cols:
                        selected_female_cols.append(female_col)
                        selected_labels.append(col.split("_")[-1])

        # 시각화
        fig = go.Figure()

        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'cyan', 'magenta']
        for idx, region in enumerate(selected_regions):
            region_row = df[df["지역"] == region]
            if region_row.empty:
                continue

            male = region_row[selected_male_cols].iloc[0].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)
            female = region_row[selected_female_cols].iloc[0].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)

            color = colors[idx % len(colors)]

            fig.add_trace(go.Bar(
                y=selected_labels,
                x=-male,
                name=f"{region} (남)",
                orientation="h",
                marker_color=color,
                legendgroup=region
            ))

            fig.add_trace(go.Bar(
                y=selected_labels,
                x=female,
                name=f"{region} (여)",
                orientation="h",
                marker_color=color,
                opacity=0.5,
                legendgroup=region,
                showlegend=False
            ))

        fig.update_layout(
            title="여러 지역 인구 피라미드 비교",
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
    st.info("왼쪽에서 연령별 인구 CSV 파일을 업로드해주세요.")
