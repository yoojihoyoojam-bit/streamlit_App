import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_KEY = "여기에_API_KEY"

st.set_page_config(page_title="날씨 앱", page_icon="🌤️")

st.title("🌤️ 실시간 날씨 & 5일 예보")

city = st.text_input("도시 입력", "Seoul")

if st.button("검색"):

    current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"

    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=kr"

    current = requests.get(current_url).json()

    if current["cod"] != 200:
        st.error("도시를 찾을 수 없습니다.")
        st.stop()

    st.subheader("현재 날씨")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🌡️ 기온", f"{current['main']['temp']}°C")

    with col2:
        st.metric("🤒 체감", f"{current['main']['feels_like']}°C")

    with col3:
        st.metric("💧 습도", f"{current['main']['humidity']}%")

    st.write("☁️", current["weather"][0]["description"])
    st.write("💨 풍속 :", current["wind"]["speed"], "m/s")

    forecast = requests.get(forecast_url).json()

    df = pd.DataFrame(forecast["list"])

    df["시간"] = pd.to_datetime(df["dt_txt"])
    df["기온"] = df["main"].apply(lambda x: x["temp"])

    fig = px.line(
        df,
        x="시간",
        y="기온",
        title="5일 기온 변화"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("예보")

    for item in forecast["list"][:10]:
        st.write(
            item["dt_txt"],
            item["weather"][0]["description"],
            f"{item['main']['temp']}°C"
        )
