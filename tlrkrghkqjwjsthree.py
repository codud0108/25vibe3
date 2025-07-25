import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="기상 통계 시각화", layout="wide")
st.title("🌦️ 지점별 기상 통계 시각화")

# 파일 업로드
uploaded_file = st.file_uploader("📂 기상 통계 CSV 파일을 업로드하세요 (예: 종관기상_지점별_연·월_통계)", type=["csv"])

if uploaded_file:
    try:
        # 여러 인코딩 시도
        encodings_to_try = ["cp949", "utf-8", "utf-8-sig"]
        for enc in encodings_to_try:
            try:
                df = pd.read_csv(uploaded_file, encoding=enc)
                break
            except:
                continue

        # 첫 번째 행을 컬럼으로 설정
        new_columns = df.iloc[0]
        df_cleaned = df[1:].copy()
        df_cleaned.columns = new_columns
        df_cleaned.columns = df_cleaned.columns.str.strip()
        df_cleaned.reset_index(drop=True, inplace=True)
        df_cleaned.rename(columns={"관측지점별(1)": "지점"}, inplace=True)

        # 시각화 항목 선택
        options = [col for col in df_cleaned.columns if col != "지점"]
        selected_col = st.selectbox("📊 시각화할 항목을 선택하세요:", options)

        # Plotly 막대 그래프
        fig = go.Figure()
        for index, row in df_cleaned.iterrows():
            try:
                y_val = float(row[selected_col])
            except:
                y_val = None
            fig.add_trace(go.Bar(
                x=[selected_col],
                y=[y_val],
                name=row["지점"]
            ))

        fig.update_layout(
            title=f"지점별 {selected_col} 비교",
            xaxis_title="항목",
            yaxis_title="값",
            barmode="group",
            template="plotly_white",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"파일 처리 중 오류 발생: {e}")
else:
    st.info("좌측 사이드바 또는 위의 버튼을 통해 기상 통계 CSV 파일을 업로드하세요.")
