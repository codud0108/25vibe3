import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

st.set_page_config(page_title="도-시-구 다중 선택 인구 피라미드", layout="wide")
st.title("👥 도-시-구 다중 선택 인구 피라미드 비교 (2025년 6월 기준)")

uploaded_file = st.file_uploader("📂 연령별 인구 데이터 (CSV, euc-kr 인코딩)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding="euc-kr")

        # 도, 시, 구 분리
        df["도"] = df["행정구역"].str.extract(r"^([가-힣]+[도시특별시광역시자치시특별자치도]+)")
        df["시"] = df["행정구역"].str.extract(r"^.+? ([가-힣]+[시군구])")
        df["구"] = df["행정구역"].str.extract(r".+? ([가-힣]+[동구면읍])")

        df["도"] = df["도"].fillna("")
        df["시"] = df["시"].fillna("")
        df["구"] = df["구"].fillna("")

        # 지역 라벨 생성
        df["지역"] = df[["도", "시", "구"]].agg(" ".join, axis=1).str.strip()

        # 🔹 사이드바: 단계별 지역 선택
        st.sidebar.header("📍 지역 선택")

        all_dos = sorted(df["도"].unique())
        selected_dos = st.sidebar.multiselect("도 선택", all_dos, default=all_dos[:1])

        filtered_si_df = df[df["도"].isin(selected_dos)]
        all_sis = sorted(filtered_si_df["시"].unique())
        selected_sis = st.sidebar.multiselect("시 선택", all_sis, default=all_sis[:2])

        filtered_gu_df = df[df["시"].isin(selected_sis)]
        all_gus = sorted(filtered_gu_df["구"].unique())
        selected_gus = st.sidebar.multiselect("구 선택 (옵션)", all_gus)

        # 🔹 지역 필터링
        region_mask = (
            df["도"].isin(selected_dos) &
            df["시"].isin(selected_sis)
        )
        if selected_gus:
            region_mask &= df["구"].isin(selected_gus)

        selected_df = df[region_mask]
        selected_regions = selected_df["지역"].unique()

        if len(selected_regions) == 0:
            st.warning("선택한 지역 조합에 해당하는 데이터가 없습니다.")
            st.stop()

        # 🔹 연령 그룹 선택
        st.sidebar.header("🎚️ 연령 그룹 선택")
        age_groups = [(f"{i}~{i+9}세", list(range(i, i+10))) for i in range(0, 100, 10)]
        age_groups.append(("100세 이상", list(range(100, 101))))
        group_names = [g[0] for g in age_groups]
        selected_groups = st.sidebar.multiselect("연령 그룹 선택", group_names, default=group_names)

        # 🔹 컬럼 처리
        male_cols = [col for col in df.columns if "남_" in col and "세" in col]
        female_cols = [col for col in df.columns if "여_" in col and "세" in col]

        def extract_age(col_name):
            match = re.search(r"(\d+)세", col_name)
            return int(match.group(1)) if match else 100

        age_mapping = {col: extract_age(col) for col in male_cols}

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

        # 🔹 그래프 생성
        fig = go.Figure()
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'cyan', 'magenta']

        for idx, region in enumerate(selected_regions):
            row = df[df["지역"] == region]
            if row.empty:
                continue

            male = row[selected_male_cols].iloc[0].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)
            female = row[selected_female_cols].iloc[0].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)

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
            title="선택된 지역 인구 피라미드 비교",
            barmode="relative",
            xaxis_title="인구수",
            yaxis_title="연령",
            xaxis_tickformat=",d",
            height=1000,
            yaxis=dict(autorange="reversed")
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
else:
    st.info("📄 좌측에서 연령별 인구 CSV 파일을 업로드해주세요.")
