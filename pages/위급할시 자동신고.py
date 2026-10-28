
import streamlit as st

st.set_page_config(
    page_title="안심벨 | 가상 신고 체험",
    page_icon="🔴",
    layout="centered",
    initial_sidebar_state="collapsed",
)

if "started" not in st.session_state:
    st.session_state.started = False

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@500;700;900&display=swap');

.stApp {
    background: #302d78;
    font-family: 'Noto Sans KR', sans-serif;
}
.block-container {
    max-width: 500px;
    padding: 15px 10px 30px;
}
.stage {
    min-height: 520px;
    background: #fff9bd;
    border: 8px dotted #ffca24;
    outline: 3px solid #f4a900;
    border-radius: 18px;
    box-shadow: inset 0 0 0 3px #fff1a0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 20px;
    box-sizing: border-box;
}
.brand {
    font-size: 15px;
    font-weight: 900;
    color: #6b5b15;
    margin-bottom: 35px;
}
.description {
    color: #766a36;
    font-size: 14px;
    line-height: 1.8;
    margin-top: 25px;
}
.demo-label {
    color: #9a3a00;
    background: #fff0cb;
    border: 1px solid #f2cb74;
    border-radius: 20px;
    padding: 7px 12px;
    font-size: 12px;
    font-weight: 900;
    margin-bottom: 25px;
}
/* 원형 START 버튼 */
div.stButton {
    display: flex;
    justify-content: center;
    width: 100%;
}
div.stButton > button {
    width: 148px !important;
    min-width: 148px !important;
    height: 148px !important;
    min-height: 148px !important;
    border-radius: 50% !important;
    border: 7px solid #fff !important;
    outline: 2px solid #d7cba4 !important;
    background: radial-gradient(
        circle at 35% 23%,
        #ff725c 0%,
        #ed2618 38%,
        #c8170c 76%,
        #a80f09 100%
    ) !important;
    color: white !important;
    font-size: 24px !important;
    font-weight: 900 !important;
    box-shadow:
        0 8px 0 #9f160e,
        0 12px 18px #5e501d66,
        inset 0 3px 5px #ffffff70 !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
}
div.stButton > button:hover {
    transform: translateY(-3px) scale(1.035);
    box-shadow:
        0 11px 0 #9f160e,
        0 15px 22px #5e501d66,
        inset 0 3px 5px #ffffff70 !important;
}
div.stButton > button:active {
    transform: translateY(5px) scale(.98);
    box-shadow: 0 2px 0 #9f160e !important;
}
div.stButton > button:focus-visible {
    outline: 4px solid #244db8 !important;
    outline-offset: 5px !important;
}
.result {
    background: white;
    color: #24417b;
    border-radius: 15px;
    padding: 18px;
    margin-top: 22px;
    font-weight: 700;
    line-height: 1.8;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="stage">
    <div class="brand">🛟 안심벨</div>
    <div class="demo-label">가상 체험 전용 · 실제 신고되지 않음</div>
</div>
""", unsafe_allow_html=True)

# 원형 버튼을 화면 중앙에 배치
if st.session_state.started:
    if st.button("↻ 다시", key="reset"):
        st.session_state.started = False
        st.rerun()
else:
    if st.button("START", type="primary", key="start"):
        st.session_state.started = True
        st.rerun()

if st.session_state.started:
    st.markdown("""
    <div class="result">
        🟢 가상 체험이 완료되었습니다.<br>
        버튼 작동을 확인했어요!<br><br>
        이 결과는 앱 내부의 시뮬레이션이며,
        실제 신고나 전화, 문자 전송은 발생하지 않습니다.
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="
    text-align:center;
    color:#ffffff;
    font-size:13px;
    line-height:1.9;
    padding:20px 8px;
">
    <b>안심벨 가상 신고 체험</b><br>
    START 버튼을 눌러 작동을 체험해 보세요.<br>
    실제 신고 기능은 포함되어 있지 않습니다.
</div>
""", unsafe_allow_html=True)
