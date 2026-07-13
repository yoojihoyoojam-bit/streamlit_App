import streamlit as st
import random

st.set_page_config(page_title="⚡ 운빨 강화", page_icon="⚔️")

st.title("⚔️ 운빨 강화 게임")
st.write("목표: +30까지 강화해보세요!")

# 최초 실행
if "level" not in st.session_state:
    st.session_state.level = 0
    st.session_state.gold = 1000
    st.session_state.best = 0
    st.session_state.log = []

level = st.session_state.level

# 검 이름
def sword_name(level):
    if level < 5:
        return "🪵 낡은 나무검"
    elif level < 10:
        return "⚔️ 강철검"
    elif level < 15:
        return "🛡️ 기사의 검"
    elif level < 20:
        return "🔥 화염검"
    elif level < 25:
        return "⚡ 번개의 검"
    elif level < 30:
        return "🌌 신화의 검"
    else:
        return "👑 전설의 에테르 블레이드"

# 성공 확률
def success_rate(level):
    if level < 5:
        return 90
    elif level < 10:
        return 70
    elif level < 15:
        return 50
    elif level < 20:
        return 35
    elif level < 25:
        return 20
    else:
        return 10

st.subheader(sword_name(level))
st.markdown(f"# +{level}")

st.progress(min(level / 30, 1.0))

st.write(f"💰 골드 : {st.session_state.gold}")
st.write(f"🏆 최고 강화 : +{st.session_state.best}")

cost = 50 + level * 20

st.write(f"강화 비용 : {cost} Gold")
st.write(f"성공 확률 : {success_rate(level)}%")

if st.button("⚒️ 강화하기"):

    if st.session_state.gold < cost:
        st.error("골드가 부족합니다.")
    else:

        st.session_state.gold -= cost

        rand = random.randint(1,100)

        # 대성공
        if rand == 1:
            st.session_state.level += 2
            st.success("🌈 대성공!! +2 강화")
        else:

            if rand <= success_rate(level):
                st.session_state.level += 1
                st.success("✨ 강화 성공!")

            else:

                # 파괴
                if level >= 20 and random.random() < 0.25:
                    st.session_state.level = 0
                    st.error("💥 검이 파괴되었습니다...")
                else:

                    if level >= 10:
                        st.session_state.level -= 1
                        st.warning("⬇️ 강화 실패! -1")
                    else:
                        st.warning("❌ 강화 실패!")

        if st.session_state.level > st.session_state.best:
            st.session_state.best = st.session_state.level

        st.session_state.log.insert(
            0,
            f"+{st.session_state.level}"
        )

if st.button("💰 골드 받기 (+500)"):
    st.session_state.gold += 500

if st.button("🔄 새 게임"):
    st.session_state.level = 0
    st.session_state.gold = 1000
    st.session_state.best = 0
    st.session_state.log = []

st.divider()

st.subheader("📜 강화 기록")

for x in st.session_state.log[:10]:
    st.write(x)

if st.session_state.level >= 30:
    st.balloons()
    st.success("🎉 축하합니다! +30 달성!")
