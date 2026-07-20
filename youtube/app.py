import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from matplotlib import font_manager
from wordcloud import WordCloud
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from collections import Counter
import requests
import re
from datetime import datetime

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="유튜브 댓글 분석기",
    page_icon="📊",
    layout="wide"
)

st.title("📊 유튜브 댓글 분석기")
st.caption("댓글 수집 · 시간대 분석 · 감성분석 · 워드클라우드")

# -----------------------------
# Secrets에서 API 읽기
# -----------------------------
API_KEY = st.secrets["YOUTUBE_API_KEY"]

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

# -----------------------------
# GitHub 폰트
# -----------------------------
FONT_PATH = "fonts/NanumGothic.ttf"

try:
    font_manager.fontManager.addfont(FONT_PATH)
    FONT_NAME = font_manager.FontProperties(fname=FONT_PATH).get_name()
    plt.rcParams["font.family"] = FONT_NAME
except:
    FONT_NAME = None

# -----------------------------
# 유튜브 ID 추출
# -----------------------------
def extract_video_id(url):

    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]

    parsed = urlparse(url)

    if parsed.hostname in [
        "www.youtube.com",
        "youtube.com"
    ]:
        return parse_qs(parsed.query)["v"][0]

    return None

# -----------------------------
# 댓글 가져오기
# -----------------------------
def get_comments(video_id, max_comments):

    comments = []

    next_page = None

    while len(comments) < max_comments:

        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            pageToken=next_page,
            textFormat="plainText",
            order="relevance"
        )

        response = request.execute()

        for item in response["items"]:

            snippet = item["snippet"]["topLevelComment"]["snippet"]

            comments.append({
                "작성자": snippet["authorDisplayName"],
                "댓글": snippet["textDisplay"],
                "좋아요": snippet["likeCount"],
                "시간": snippet["publishedAt"]
            })

            if len(comments) >= max_comments:
                break

        next_page = response.get("nextPageToken")

        if next_page is None:
            break

    return pd.DataFrame(comments)

# -----------------------------
# 영상 정보
# -----------------------------
def get_video_info(video_id):

    response = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    ).execute()

    item = response["items"][0]

    return {
        "title": item["snippet"]["title"],
        "channel": item["snippet"]["channelTitle"],
        "views": int(item["statistics"].get("viewCount",0)),
        "likes": int(item["statistics"].get("likeCount",0))
    }

# -----------------------------
# 사이드바
# -----------------------------
st.sidebar.header("설정")

video_url = st.sidebar.text_input(
    "유튜브 링크"
)

comment_count = st.sidebar.slider(
    "댓글 개수",
    50,
    1000,
    300,
    50
)

run = st.sidebar.button("분석 시작")

# -----------------------------
# 실행
# -----------------------------
if run:

    video_id = extract_video_id(video_url)

    if video_id is None:

        st.error("유튜브 링크가 올바르지 않습니다.")

        st.stop()

    info = get_video_info(video_id)

    col1, col2 = st.columns([2,1])

    with col1:

        st.subheader(info["title"])

        st.components.v1.iframe(
            f"https://www.youtube.com/embed/{video_id}",
            height=500
        )

    with col2:

        st.metric("채널", info["channel"])
        st.metric("조회수", f"{info['views']:,}")
        st.metric("좋아요", f"{info['likes']:,}")

    with st.spinner("댓글 가져오는 중..."):

        df = get_comments(
            video_id,
            comment_count
        )

    st.success(f"{len(df)}개의 댓글을 가져왔습니다.")

    st.dataframe(
        df,
        use_container_width=True,
        height=400
    )

    st.session_state["comments"] = df

    # -----------------------------
    # 시간 데이터 변환
    # -----------------------------
    df["시간"] = pd.to_datetime(df["시간"])

    df["날짜"] = df["시간"].dt.date
    df["시"] = df["시간"].dt.hour
    df["요일"] = df["시간"].dt.day_name()

    # -----------------------------
    # 기본 통계
    # -----------------------------
    st.divider()
    st.header("📈 댓글 통계")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("댓글 수", len(df))
    c2.metric("평균 좋아요", round(df["좋아요"].mean(), 2))
    c3.metric("최대 좋아요", df["좋아요"].max())
    c4.metric("작성자 수", df["작성자"].nunique())

    # -----------------------------
    # 시간대별 댓글
    # -----------------------------
    st.subheader("🕒 시간대별 댓글 작성 추이")

    hour_df = (
        df.groupby("시")
        .size()
        .reset_index(name="댓글수")
        .sort_values("시")
    )

    fig = px.bar(
        hour_df,
        x="시",
        y="댓글수",
        text="댓글수",
        color="댓글수",
        color_continuous_scale="Blues"
    )

    fig.update_layout(
        xaxis_title="시간",
        yaxis_title="댓글 수",
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -----------------------------
    # 날짜별 댓글
    # -----------------------------
    st.subheader("📅 날짜별 댓글 추이")

    date_df = (
        df.groupby("날짜")
        .size()
        .reset_index(name="댓글수")
    )

    fig2 = px.line(
        date_df,
        x="날짜",
        y="댓글수",
        markers=True
    )

    fig2.update_layout(
        height=450
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    # -----------------------------
    # 요일별 댓글
    # -----------------------------
    st.subheader("📆 요일별 댓글")

    order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    week = (
        df.groupby("요일")
        .size()
        .reindex(order)
        .fillna(0)
        .reset_index(name="댓글수")
    )

    fig3 = px.bar(
        week,
        x="요일",
        y="댓글수",
        text="댓글수",
        color="댓글수",
        color_continuous_scale="Viridis"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    # -----------------------------
    # 좋아요 TOP10
    # -----------------------------
    st.divider()
    st.header("👍 좋아요 많은 댓글 TOP10")

    top10 = (
        df.sort_values(
            "좋아요",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top10[
            [
                "작성자",
                "좋아요",
                "댓글"
            ]
        ],
        use_container_width=True,
        height=420
    )

    # -----------------------------
    # 댓글 길이 분석
    # -----------------------------
    st.subheader("✍️ 댓글 길이 분포")

    df["댓글길이"] = df["댓글"].str.len()

    fig4 = px.histogram(
        df,
        x="댓글길이",
        nbins=30
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

    st.session_state["comments"] = df

    # =====================================================
    # 형태소 분석
    # =====================================================

    st.divider()
    st.header("☁️ 댓글 키워드 분석")

    stopwords = [
        "것","수","정도","진짜","그냥","너무","정말","영상",
        "이번","오늘","저는","제가","ㅋㅋ","ㅎㅎ","ㅠㅠ",
        "입니다","있습니다","합니다","있는","하는","하고",
        "에서","으로","까지","그리고","하지만","입니다",
        "이거","저거","우리","여기","저기","때문","사람",
        "하나","같은","이런","그런","더","좀","잘","왜",
        "또","이제","진심","완전","진짜로","ㅋㅋㅋ","ㅎㅎㅎ"
    ]
    text = " ".join(df["댓글"].astype(str))

    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@[A-Za-z0-9_]+", "", text)
    text = re.sub(r"[^가-힣 ]", " ", text)

    words = re.findall(r"[가-힣]{2,}", text)

    words = [w for w in words if w not in stopwords]

    counter = Counter(words)


    # =====================================================
    # TOP30 단어
    # =====================================================

    st.subheader("🔥 가장 많이 나온 단어")

    word_df = pd.DataFrame(
        counter.most_common(30),
        columns=["단어","빈도"]
    )

    fig = px.bar(
        word_df,
        x="단어",
        y="빈도",
        text="빈도",
        color="빈도",
        color_continuous_scale="Teal"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # =====================================================
    # 워드클라우드
    # =====================================================

    st.subheader("☁️ 한글 워드클라우드")

    wc = WordCloud(

        font_path=FONT_PATH,

        width=1200,

        height=700,

        background_color="white",

        colormap="tab20",

        max_words=200

    ).generate_from_frequencies(counter)

    fig, ax = plt.subplots(figsize=(16,8))

    ax.imshow(wc)

    ax.axis("off")

    st.pyplot(fig)

    # =====================================================
    # 키워드 표
    # =====================================================

    with st.expander("키워드 빈도 보기"):

        st.dataframe(
            word_df,
            use_container_width=True,
            height=500
        )

    # =====================================================
    # 감성분석
    # =====================================================

    st.divider()

    st.header("😊 댓글 반응 분석")

    positive_words = [

        "좋다","최고","감사","멋지다","대박","사랑",

        "웃기다","행복","응원","훌륭","잘","재밌다",

        "추천","최강","감동","완벽","짱","기대",

        "굿","예쁘다","훌륭하다"

    ]

    negative_words = [

        "별로","싫다","최악","실망","구리다","화난",

        "짜증","노잼","못","망했다","아쉽","욕",

        "답답","불편","비추","억지","실수","문제",

        "이상","쓰레기"

    ]

    positive = 0

    negative = 0

    neutral = 0

    for text in df["댓글"]:

        text = str(text)

        p = sum(

            word in text

            for word in positive_words

        )

        n = sum(

            word in text

            for word in negative_words

        )

        if p > n:

            positive += 1

        elif n > p:

            negative += 1

        else:

            neutral += 1

    senti = pd.DataFrame({

        "감정":[

            "긍정",

            "부정",

            "중립"

        ],

        "개수":[

            positive,

            negative,

            neutral

        ]

    })

    fig = px.pie(

        senti,

        values="개수",

        names="감정",

        hole=0.45

    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

    c1,c2,c3 = st.columns(3)

    c1.metric("😊 긍정", positive)

    c2.metric("😐 중립", neutral)

    c3.metric("😡 부정", negative)

    st.session_state["word_df"] = word_df

    # =====================================================
    # 댓글 검색
    # =====================================================

    st.divider()
    st.header("🔍 댓글 검색")

    keyword = st.text_input("검색할 단어를 입력하세요.")

    if keyword:

        result = df[
            df["댓글"].str.contains(
                keyword,
                case=False,
                na=False
            )
        ]

        st.write(f"검색 결과 : {len(result)}개")

        st.dataframe(
            result,
            use_container_width=True,
            height=400
        )

    # =====================================================
    # CSV 다운로드
    # =====================================================

    st.divider()
    st.header("📥 결과 다운로드")

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="댓글 CSV 다운로드",
        data=csv,
        file_name="youtube_comments.csv",
        mime="text/csv"
    )

    keyword_csv = word_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="키워드 빈도 CSV 다운로드",
        data=keyword_csv,
        file_name="keyword_frequency.csv",
        mime="text/csv"
    )

    # =====================================================
    # AI 스타일 요약
    # =====================================================

    st.divider()
    st.header("📋 분석 결과 요약")

    top_keyword = word_df.iloc[0]["단어"]

    top_count = word_df.iloc[0]["빈도"]

    sentiment = max(
        [
            ("긍정", positive),
            ("부정", negative),
            ("중립", neutral)
        ],
        key=lambda x:x[1]
    )[0]

    busiest_hour = (
        hour_df.sort_values(
            "댓글수",
            ascending=False
        )
        .iloc[0]["시"]
    )

    st.success(
        f"""
### 분석 결과

• 총 댓글 수 : {len(df):,}개

• 가장 많이 등장한 단어 : **{top_keyword}**

• 등장 횟수 : **{top_count}회**

• 댓글이 가장 많이 작성된 시간 : **{busiest_hour}시**

• 전체 댓글 분위기 : **{sentiment}**

• 분석 완료!
"""
    )

    # =====================================================
    # TOP20 키워드
    # =====================================================

    st.divider()

    st.header("🏆 TOP20 키워드")

    cols = st.columns(4)

    for i,(word,count) in enumerate(counter.most_common(20)):

        cols[i%4].metric(
            word,
            count
        )

    # =====================================================
    # 좋아요 TOP5
    # =====================================================

    st.divider()

    st.header("❤️ 좋아요 BEST 댓글")

    best = (
        df.sort_values(
            "좋아요",
            ascending=False
        )
        .head(5)
    )

    for i,row in best.iterrows():

        with st.container():

            st.markdown(
                f"""
### 👍 {row['좋아요']}개

{row['댓글']}

작성자 : {row['작성자']}
"""
            )

            st.divider()

    # =====================================================
    # Footer
    # =====================================================

    st.caption(
        "Made with Streamlit · YouTube Data API v3"
    )
