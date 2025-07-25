import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="기상 통계 시각화", layout="wide")
st.title("🌡️ 지점별 기상 통계 시계열 그래프")

uploaded_file = st.file_uploader("📂 기상 통계 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    try:
        # 파일 읽기
        df = pd.read_csv(uploaded_file, encoding="utf-8")

        # 첫 번째 행을 컬럼으로 사용
        df.columns = df.iloc[0]
        df = df[1:].copy()
        df.columns.name = None
        df.reset_index(drop=True, inplace=True)
        df.rename(columns={"관측지점별(1)": "지점"}, inplace=True)
        df.columns = df.columns.str.strip()

        # 지점 선택
        unique_stations = df["지점"].unique().tolist()
        selected_stations = st.multiselect("📍 시각화할 지점을 선택하세요:", unique_stations, default=unique_stations[:3])

        # 날짜 컬럼 추출 (yyyy.mm.dd 형태만 선택)
        date_columns = [col for col in df.columns if "." in col and col.count(".") == 2]

        if not selected_stations:
            st.warning("⚠️ 최소 하나 이상의 지점을 선택해주세요.")
        else:
            fig = go.Figure()

            for station in selected_stations:
                row = df[df["지점"] == station].iloc[0]
                y = []
                x = []

                for date_col in date_columns:
                    try:
                        y_val = float(row[date_col])
                        y.append(y_val)
                        x.append(date_col)
                    except:
                        continue

                fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode="lines+markers",
                    name=station
                ))

            fig.update_layout(
                title="지점별 기상 통계 시계열 변화",
                xaxis_title="날짜",
                yaxis_title="값",
                template="plotly_white",
                height=600
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ 파일 처리 중 오류: {e}")
else:
    st.info("좌측에서 CSV 파일을 업로드하면 자동으로 시각화됩니다.")
