import streamlit as st
import random

st.set_page_config(
    page_title="💸 거지 탈출",
    page_icon="💰",
    layout="wide"
)

# -------------------------------
# 최초 실행
# -------------------------------

if "money" not in st.session_state:
    st.session_state.money = 0
    st.session_state.energy = 100
    st.session_state.happy = 100
    st.session_state.day = 1
    st.session_state.job = "노숙자"
    st.session_state.level = 1
    st.session_state.bike = False

# -------------------------------

def next_day():
    st.session_state.day += 1

def job_upgrade():
    money = st.session_state.money

    if money >= 1000000:
        st.session_state.job = "👑 CEO"

    elif money >= 300000:
        st.session_state.job = "💻 개발자"

    elif money >= 100000:
        st.session_state.job = "🛵 배달기사"

    elif money >= 30000:
        st.session_state.job = "🍔 편의점"

    elif money >= 10000:
        st.session_state.job = "📮 전단지 알바"

    else:
        st.session_state.job = "🧍 노숙자"

job_upgrade()

# -------------------------------

st.title("💸 거지 탈출")

col1,col2,col3,col4 = st.columns(4)

col1.metric("💰 돈",f"{st.session_state.money:,} 원")
col2.metric("❤️ 체력",st.session_state.energy)
col3.metric("😊 행복",st.session_state.happy)
col4.metric("📅 Day",st.session_state.day)

st.progress(st.session_state.energy/100)

st.info(f"현재 직업 : {st.session_state.job}")

page = st.sidebar.radio(
    "메뉴",
    [
        "🏠 홈",
        "💼 일하기",
        "🎮 미션",
        "🛒 상점"
    ]
)

# -------------------------------
# 홈
# -------------------------------

if page=="🏠 홈":

    st.subheader("오늘의 목표")

    st.checkbox("돈 1만원 모으기",st.session_state.money>=10000)

    st.checkbox("돈 10만원 모으기",st.session_state.money>=100000)

    st.checkbox("CEO 되기",st.session_state.job=="👑 CEO")

    st.success("부자가 되어보자!")

# -------------------------------
# 일하기
# -------------------------------

elif page=="💼 일하기":

    st.subheader("돈 벌기")

    if st.button("🥣 구걸하기"):

        earn=random.randint(500,2000)

        st.session_state.money+=earn

        st.session_state.energy-=5

        st.success(f"{earn}원을 벌었습니다!")

        next_day()

    if st.button("📮 전단지 알바"):

        if st.session_state.money<10000:

            st.warning("1만원 이상 있어야 가능합니다.")

        else:

            earn=random.randint(3000,7000)

            st.session_state.money+=earn

            st.session_state.energy-=15

            st.success(f"{earn}원 획득!")

            next_day()

    if st.button("🍔 편의점 알바"):

        if st.session_state.money<30000:

            st.warning("3만원 이상 모아야 가능합니다.")

        else:

            earn=random.randint(8000,15000)

            st.session_state.money+=earn

            st.session_state.energy-=20

            st.success(f"{earn}원 벌었습니다!")

            next_day()

    if st.button("🛵 배달하기"):

        if st.session_state.money<100000:

            st.warning("10만원 이상 있어야 가능합니다.")

        else:

            earn=random.randint(15000,30000)

            if st.session_state.bike:
                earn=int(earn*1.5)

            st.session_state.money+=earn

            st.session_state.energy-=25

            st.success(f"{earn}원 획득!")

            next_day()

# -------------------------------
# 미션
# -------------------------------

elif page=="🎮 미션":

    missions=[
        ("🧹 공원 청소",6000,80),
        ("📦 심부름",12000,70),
        ("🚚 이사 돕기",25000,55),
        ("🪟 유리 닦기",18000,65),
        ("🐶 강아지 산책",9000,90)
    ]

    mission=random.choice(missions)

    st.subheader(mission[0])

    st.write(f"보상 : {mission[1]:,}원")

    st.write(f"성공확률 : {mission[2]}%")

    if st.button("도전하기"):

        if random.randint(1,100)<=mission[2]:

            st.success("성공!")

            st.session_state.money+=mission[1]

        else:

            st.error("실패!")

            st.session_state.energy-=15

        next_day()

# -------------------------------
# 상점
# -------------------------------

elif page=="🛒 상점":

    st.subheader("상점")

    if st.button("🍜 라면 (2,000원)"):

        if st.session_state.money>=2000:

            st.session_state.money-=2000

            st.session_state.energy=min(
                100,
                st.session_state.energy+20
            )

            st.success("체력 회복!")

        else:

            st.error("돈 부족")

    if st.button("🍔 햄버거 (7,000원)"):

        if st.session_state.money>=7000:

            st.session_state.money-=7000

            st.session_state.happy=min(
                100,
                st.session_state.happy+20
            )

            st.success("행복 증가!")

        else:

            st.error("돈 부족")

    if st.button("🚲 자전거 (50,000원)"):

        if st.session_state.money>=50000 and not st.session_state.bike:

            st.session_state.money-=50000

            st.session_state.bike=True

            st.success("배달 수익이 50% 증가했습니다!")

        elif st.session_state.bike:

            st.info("이미 구매했습니다.")

        else:

            st.error("돈 부족")

# -------------------------------

if st.session_state.energy<=0:

    st.error("체력이 모두 소진되었습니다.")

    if st.button("😴 하루 쉬기"):

        st.session_state.energy=100

        st.session_state.day+=1
