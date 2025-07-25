import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="📊 평균연령 시각화", layout="wide")
st.title("📊 2025년 6월 지역별 평균연령 (남녀 비교)")

# 파일 업로드
uploaded_file = st.file_uploader("📂 CSV 파일 업로드 (euc-kr 인코딩)", type=["csv"])

if uploaded_file is not None:
    try:
        # 데이터 로딩
        df = pd.read_csv(uploaded_file, encoding="cp949")

        # 시/구까지만 필터링 (괄호가 1번만 등장하는 행정구역)
        df = df[df["행정구역"].str.count(r"\(") == 1].copy()

        # 행정구역 이름에서 괄호 제거
        df["행정구역"] = df["행정구역"].str.replace(r"\s*\(.*\)", "", regex=True)

        # 컬럼 이름 간편화
        df["남자 평균연령"] = pd.to_numeric(df["2025년06월_남자 평균연령"], errors="coerce")
        df["여자 평균연령"] = pd.to_numeric(df["2025년06월_여자 평균연령"], errors="coerce")

        # 선택 필터 (선택적으로 특정 시도만)
        selected_region = st.multiselect(
            "📍 특정 시도 선택 (선택하지 않으면 전체 표시)",
            options=sorted(df["행정구역"].str.extract(r"^([가-힣]+도|[가-힣]+시)")[0].dropna().unique()),
        )

        if selected_region:
            df = df[df["행정구역"].str.startswith(tuple(selected_region))]

        # Melt for grouped bar chart
        df_melted = df.melt(id_vars="행정구역", value_vars=["남자 평균연령", "여자 평균연령"],
                            var_name="성별", value_name="평균연령")

        # Plotly 그래프
        fig = px.bar(
            df_melted,
            x="행정구역",
            y="평균연령",
            color="성별",
            barmode="group",
            title="2025년 6월 지역별 평균 연령 (남녀 비교)",
            labels={"행정구역": "지역", "평균연령": "평균 연령 (세)"},
        )
        fig.update_layout(xaxis_tickangle=-45, height=600)

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
else:
    st.info("좌측 사이드바 또는 위에서 CSV 파일을 업로드해주세요.")
