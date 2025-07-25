import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# 페이지 설정
st.set_page_config(page_title="📊 법정동별 인구 증감 시각화", layout="wide")
st.title("📊 2025년 6월 법정동별 인구 증감 및 전월/당월 비교")

# 파일 업로드
uploaded_file = st.file_uploader("📂 CSV 파일을 업로드하세요 (euc-kr 인코딩)", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding="euc-kr")
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding="utf-8")

    # 숫자형 변환
    for col in [
        "2025년06월_전월인구수_계", "2025년06월_당월인구수_계",
        "2025년06월_전월인구수_남자인구수", "2025년06월_전월인구수_여자인구수",
        "2025년06월_당월인구수_남자인구수", "2025년06월_당월인구수_여자인구수",
        "2025년06월_인구증감_계", "2025년06월_인구증감_남자인구수", "2025년06월_인구증감_여자인구수"
    ]:
        df[col] = df[col].astype(str).str.replace(",", "").astype(int)

    # 도/시/구 분리
    df["도"] = df["법정구역"].str.extract(r"^([가-힣]+[도시특별시광역시자치시특별자치도]+)")
    df["시"] = df["법정구역"].str.extract(r"^.+? ([가-힣]+[시군구])")
    df["구"] = df["법정구역"].str.extract(r"^.+? .+? ([가-힣]+동|[가-힣]+면|[가-힣]+리)?")

    # 사이드바 필터링
    st.sidebar.header("🔍 지역 선택")

    selected_dos = st.sidebar.multiselect("도 선택", sorted(df["도"].dropna().unique()))
    filtered_df = df[df["도"].isin(selected_dos)] if selected_dos else df.copy()

    selected_sis = st.sidebar.multiselect("시 선택", sorted(filtered_df["시"].dropna().unique()))
    filtered_df = filtered_df[filtered_df["시"].isin(selected_sis)] if selected_sis else filtered_df

    gu_options = sorted(filtered_df["구"].dropna().unique())
    selected_gus = st.sidebar.multiselect("구/동 선택", ["전체"] + gu_options)
    if selected_gus and "전체" not in selected_gus:
        filtered_df = filtered_df[filtered_df["구"].isin(selected_gus)]

    # 성별 선택
    st.sidebar.header("👥 성별 선택")
    gender_option = st.sidebar.radio("시각화할 인구 증감 항목:", ["전체", "남자", "여자"])

    if filtered_df.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
        st.stop()

    # 성별에 따른 컬럼 선택
    if gender_option == "전체":
        delta_col = "2025년06월_인구증감_계"
        prev_col = "2025년06월_전월인구수_계"
        curr_col = "2025년06월_당월인구수_계"
        y_label = "전체 인구 증감"
    elif gender_option == "남자":
        delta_col = "2025년06월_인구증감_남자인구수"
        prev_col = "2025년06월_전월인구수_남자인구수"
        curr_col = "2025년06월_당월인구수_남자인구수"
        y_label = "남자 인구 증감"
    else:
        delta_col = "2025년06월_인구증감_여자인구수"
        prev_col = "2025년06월_전월인구수_여자인구수"
        curr_col = "2025년06월_당월인구수_여자인구수"
        y_label = "여자 인구 증감"

    # 시각화 준비
    x = filtered_df["법정구역"]
    bar_y = filtered_df[delta_col]
    line_prev = filtered_df[prev_col]
    line_curr = filtered_df[curr_col]

    # 이중 축 plotly 그래프 구성
    fig = go.Figure()

    # 막대그래프 (인구 증감)
    fig.add_trace(go.Bar(
        x=x,
        y=bar_y,
        name=y_label,
        marker_color='indianred',
        yaxis='y1'
    ))

    # 라인그래프 (전월 인구)
    fig.add_trace(go.Scatter(
        x=x,
        y=line_prev,
        name="전월 인구",
        mode='lines+markers',
        line=dict(color='blue'),
        yaxis='y2'
    ))

    # 라인그래프 (당월 인구)
    fig.add_trace(go.Scatter(
        x=x,
        y=line_curr,
        name="당월 인구",
        mode='lines+markers',
        line=dict(color='green'),
        yaxis='y2'
    ))

    # 레이아웃 설정
    fig.update_layout(
        title="📊 인구 증감 + 전월/당월 인구 비교",
        xaxis=dict(title="지역", tickangle=-45),
        yaxis=dict(title="인구 증감", side='left'),
        yaxis2=dict(
            title="전월/당월 인구수",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        legend=dict(x=0.01, y=1.05, orientation="h"),
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("📁 좌측 사이드바에서 CSV 파일을 업로드해주세요.")
