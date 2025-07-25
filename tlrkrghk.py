import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 페이지 설정
st.set_page_config(page_title="도/시/구 인구 피라미드", layout="wide")
st.title("👥 도-시-구 단위 연령별 인구 피라미드 (2025년 6월 기준)")

# CSV 업로드
uploaded_file = st.file_uploader("📂 연령별 인구 데이터 (CSV, euc-kr 인코딩)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding="euc-kr")

        # 지역 정보 분리
        df = df.copy()
        df["도"] = df["행정구역"].str.extract(r"^([가-힣]+[도|시|특별시|광역시|자치시|자치도|특별자치도])")
        df["시"] = df["행정구역"].str.extract(r"^.+? ([가-힣]+[시|군|구])")
        df["구"] = df["행정구역"].str.extract(r".+? ([가-힣]+동|[가-힣]+구|[가-힣]+면|[가-힣]+읍)")

        # 사이드바 선택 UI
        st.sidebar.header("📍 지역 선택")
        selected_do = st.sidebar.selectbox("도 (광역단체)", sorted(df["도"].dropna().unique()))
        filtered_si = df[df["도"] == selected_do]["시"].dropna().unique()
        selected_si = st.sidebar.selectbox("시 (기초단체)", sorted(filtered_si))

        filtered_gu = df[(df["도"] == selected_do) & (df["시"] == selected_si)]["구"].dropna().unique()
        gu_options = sorted(filtered_gu) if len(filtered_gu) > 0 else ["(해당 없음)"]
        selected_gu = st.sidebar.selectbox("구/동/읍/면", gu_options)

        # 대상 행정구역 이름 찾기
        candidates = df[
            (df["도"] == selected_do) &
            (df["시"] == selected_si)
        ]
        if selected_gu != "(해당 없음)":
            candidates = candidates[candidates["구"] == selected_gu]

        if candidates.empty:
            st.warning("선택한 행정구역에 해당하는 데이터가 없습니다.")
            st.stop()

        selected_row = candidates.iloc[0]

        # 연령 그룹 선택
        st.sidebar.header("🎚️ 연령 그룹 선택")
        age_groups = [(f"{i}~{i+9}세", list(range(i, i+10))) for i in range(0, 100, 10)]
        age_groups.append(("100세 이상", list(range(100, 101))))
        group_names = [g[0] for g in age_groups]
        selected_groups = st.sidebar.multiselect("연령 그룹 선택", group_names, default=group_names)

        # 연령 컬럼 정리
        male_cols = [col for col in df.columns if "남_" in col and "세" in col]
        female_cols = [col for col in df.columns if "여_" in col and "세" in col]

        def extract_age(col_name):
            match = re.search(r"(\d+)세", col_name)
            return int(match.group(1)) if match else 100

        age_mapping = {col: extract_age(col) for col in male_cols}

        # 선택한 연령 범위에 해당하는 컬럼만 추출
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

        # 데이터 전처리
        male_counts = selected_row[selected_male_cols].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)
        female_counts = selected_row[selected_female_cols].fillna(0).astype(str).str.replace(",", "").astype(float).astype(int)

        # 인구 피라미드 시각화
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

        title_text = f"{selected_do} {selected_si}"
        if selected_gu != "(해당 없음)":
            title_text += f" {selected_gu}"
        fig.update_layout(
            title=f"{title_text} 인구 피라미드",
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
