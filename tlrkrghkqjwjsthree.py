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

        # 첫 행을 컬럼으로
        df.columns = df.iloc[0]
        df = df[1:].copy()
        df.columns.name = None
        df.reset_index(drop=True, inplace=True)
        df.rename(columns={"관측지점별(1)": "지점"}, inplace=True)
        df.columns = df.columns.str.strip()

        # ---------- 항목(변수) 선택 ----------
        variable_row = df[df["지점"] == "지점"]  # 1행 아래 항목 정보 있는 행
        df = df[df["지점"] != "지점"]  # 실제 데이터만 남김
        variable_row = variable_row.iloc[0]  # 시리즈로

        # 날짜 컬럼 중 시계열에 해당하는 열 추출
        date_columns = [col for col in df.columns if "." in col and col.count(".") == 2]

        # 날짜별 항목 리스트 추출
        available_metrics = sorted(set([variable_row[col] for col in date_columns if variable_row[col] != "-"]))

        selected_metric = st.selectbox("📈 시각화할 항목을 선택하세요:", available_metrics)

        # ---------- 지점 선택 ----------
        unique_stations = df["지점"].unique().tolist()
        selected_stations = st.multiselect("📍 시각화할 지점을 선택하세요:", unique_stations, default=unique_stations[:3])

        if not selected_stations:
            st.warning("⚠️ 최소 하나 이상의 지점을 선택해주세요.")
        else:
            # 선택한 항목에 해당하는 날짜 컬럼만 선택
            selected_date_cols = [col for col in date_columns if variable_row[col] == selected_metric]

            fig = go.Figure()

            for station in selected_stations:
                row = df[df["지점"] == station].iloc[0]
                y = []
                x = []

                for date_col in selected_date_cols:
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
                title=f"{selected_metric} - 지점별 시계열 변화",
                xaxis_title="날짜",
                yaxis_title=selected_metric,
                template="plotly_white",
                height=600
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ 파일 처리 중 오류: {e}")
else:
    st.info("좌측에서 CSV 파일을 업로드하면 자동으로 시각화됩니다.")
