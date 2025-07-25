import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

st.set_page_config(page_title="컴퓨터·태블릿 활동 분석", layout="wide")
st.title("💻 성별에 따른 컴퓨터·태블릿 활용 활동 비율 (2024)")

# 파일 업로드
uploaded_file = st.file_uploader("📂 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    # CSV 파일 디코딩 (euc-kr 또는 utf-8 시도)
    try:
        # 바이너리 → 텍스트로 변환
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        df = pd.read_csv(stringio)
    except UnicodeDecodeError:
        stringio = io.StringIO(uploaded_file.getvalue().decode("euc-kr"))
        df = pd.read_csv(stringio)

    # 첫 번째 행을 컬럼으로 설정
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)

    # 성별 필터링
    gender_df = df[df["특성별(1)"] == "성별"]

    # 활동 항목 컬럼명
    activity_columns = [
        '영상 미디어 보기 (%)',
        '게임 하기 (%)',
        'SNS 하기 (%)',
        '영상 제작 (%)',
        '혼자 공부하기 (%)',
        '음악듣기 (%)',
        '책읽기 (%)',
        '그림 그리기 (%)',
        '기타 (%)',
        '컴퓨터·태블릿 PC없음 (%)'
    ]

    # 남자, 여자 데이터
    male_row = gender_df[gender_df["특성별(2)"] == "남자"]
    female_row = gender_df[gender_df["특성별(2)"] == "여자"]

    # 비율 추출
    male_values = [float(male_row[col].values[0]) for col in activity_columns]
    female_values = [float(female_row[col].values[0]) for col in activity_columns]

    # Plotly 그래프
    fig = go.Figure()
    fig.add_trace(go.Bar(x=activity_columns, y=male_values, name="남자", marker_color="blue"))
    fig.add_trace(go.Bar(x=activity_columns, y=female_values, name="여자", marker_color="pink"))

    fig.update_layout(
        title="성별별 주요 활동 비율 비교",
        xaxis_title="활동명",
        yaxis_title="비율 (%)",
        barmode="group"
    )

    # 시각화 출력
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("왼쪽 사이드바에서 데이터를 업로드하세요. (예: 컴퓨터·태블릿 활동 통계 CSV)")
