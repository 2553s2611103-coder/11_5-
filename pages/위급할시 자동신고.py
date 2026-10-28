
import streamlit as st
from datetime import datetime
import html

# ---------------------------------------
# 기본 설정
# ---------------------------------------
st.set_page_config(
    page_title="안심벨 | 장애인 안전 신고",
    page_icon="🆘",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------
# 스타일
# ---------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}
.stApp {
    background: linear-gradient(180deg, #edf4ff 0%, #ffffff 48%);
}
.block-container {
    max-width: 720px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}
.brand {
    display: inline-block;
    background: #dce9ff;
    color: #204fbd;
    padding: 8px 15px;
    border-radius: 30px;
    font-weight: 900;
    font-size: 14px;
}
.hero {
    text-align: center;
    padding: 22px 8px 12px;
}
.hero h1 {
    color: #16366f;
    font-size: 36px;
    font-weight: 900;
    margin: 12px 0 8px;
}
.hero p {
    color: #52627b;
    font-size: 17px;
    line-height: 1.7;
}
.section-title {
    color: #18396f;
    font-size: 20px;
    font-weight: 900;
    margin: 20px 0 10px;
}
.info-card {
    background: white;
    border: 1px solid #dce6f5;
    border-radius: 18px;
    padding: 17px;
    margin: 10px 0;
}
div.stButton > button {
    width: 100%;
    min-height: 58px;
    border-radius: 15px;
    font-size: 18px;
    font-weight: 900;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 7px 18px #18396f25;
}
div.stButton > button[kind="primary"] {
    background: #e32636;
    color: white;
    border: none;
    min-height: 76px;
    font-size: 23px;
}
div.stButton > button[kind="primary"]:hover {
    background: #c91d2c;
}
a.emergency-link {
    display: block;
    text-align: center;
    padding: 17px;
    margin: 8px 0;
    border-radius: 15px;
    text-decoration: none;
    font-size: 19px;
    font-weight: 900;
}
a.red-link {
    color: white;
    background: #b91c2b;
}
a.blue-link {
    color: #1746a2;
    background: #e2edff;
    border: 1px solid #c6d9ff;
}
.small-note {
    color: #5e6b7f;
    font-size: 13px;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------
# 세션 상태 초기화
# ---------------------------------------
if "reports" not in st.session_state:
    st.session_state.reports = []

if "active_report" not in st.session_state:
    st.session_state.active_report = None

# ---------------------------------------
# 상단 화면
# ---------------------------------------
st.markdown('<div class="brand">🛟 안심벨 SAFETY</div>',
            unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div style="font-size:58px;">🆘</div>
    <h1>도움이 필요하신가요?</h1>
    <p>
        위험한 순간에는 아래 신고 버튼을 누르세요.<br>
        복잡한 절차 없이 도움을 요청할 수 있습니다.
    </p>
</div>
""", unsafe_allow_html=True)

st.error(
    "🚨 지금 생명이 위험하다면 아래 '119 전화 연결'을 이용하세요. "
    "이 앱의 접수 버튼만으로 119에 신고가 전달되지는 않습니다."
)

# ---------------------------------------
# 신고 정보 입력
# ---------------------------------------
st.markdown('<div class="section-title">📋 어떤 도움이 필요하신가요?</div>',
            unsafe_allow_html=True)

reason = st.radio(
    "위험 상황 선택",
    [
        "🧍 넘어짐 또는 낙상",
        "♿ 움직이기 어려움",
        "⚠️ 주변의 위협",
        "🆘 기타 긴급 상황",
    ],
    index=0,
)

location = st.text_input(
    "현재 위치 (선택)",
    placeholder="예: 천안시 ○○동, ○○아파트 101동",
    help="가능하다면 구조자가 찾을 수 있는 위치를 적어 주세요.",
)

detail = st.text_area(
    "추가 상황 설명 (선택)",
    placeholder="예: 혼자 이동할 수 없어요. 현관 앞에 있어요.",
    max_chars=500,
    height=100,
)

st.markdown('<div class="section-title">📞 보호자 연락처 (선택)</div>',
            unsafe_allow_html=True)

guardian_phone = st.text_input(
    "보호자 전화번호",
    placeholder="예: 01012345678",
    help="전화번호는 이 앱의 현재 화면에서만 사용합니다.",
)

# ---------------------------------------
# 신고 접수
# ---------------------------------------
st.markdown("<br>", unsafe_allow_html=True)

if st.button("🆘  긴급 도움 요청", type="primary",
             use_container_width=True):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = {
        "id": f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "time": now,
        "reason": reason,
        "location": location.strip() or "위치 미입력",
        "detail": detail.strip() or "추가 설명 없음",
        "phone": guardian_phone.strip(),
        "status": "앱 내부 접수",
    }

    st.session_state.reports.insert(0, report)
    st.session_state.active_report = report["id"]

if st.session_state.active_report:
    active = next(
        (
            item for item in st.session_state.reports
            if item["id"] == st.session_state.active_report
        ),
        None,
    )

    if active:
        st.success("앱 내부에 신고 요청이 기록되었습니다.")
        st.markdown(
            f"""
            <div class="info-card">
                <h3>✅ 신고 요청 내용</h3>
                <b>접수 시각</b>: {html.escape(active['time'])}<br>
                <b>상황</b>: {html.escape(active['reason'])}<br>
                <b>위치</b>: {html.escape(active['location'])}<br>
                <b>설명</b>: {html.escape(active['detail'])}<br>
                <b>상태</b>: 앱 내부 접수 (외부 전송 안 됨)
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("↩️ 잘못 누른 신고 취소", use_container_width=True):
            st.session_state.reports = [
                item for item in st.session_state.reports
                if item["id"] != st.session_state.active_report
            ]
            st.session_state.active_report = None
            st.rerun()

# ---------------------------------------
# 긴급 연락
# ---------------------------------------
st.markdown('<div class="section-title">☎️ 바로 연락하기</div>',
            unsafe_allow_html=True)

st.markdown(
    '<a class="emergency-link red-link" href="tel:119">'
    '🚑 119 전화 연결</a>',
    unsafe_allow_html=True,
)

# 전화번호는 숫자와 선택적 + 기호만 허용
normalized_phone = guardian_phone.strip()
if normalized_phone.startswith("+"):
    normalized_phone = "+" + "".join(
        ch for ch in normalized_phone[1:] if ch.isdigit()
    )
else:
    normalized_phone = "".join(
        ch for ch in normalized_phone if ch.isdigit()
    )

if normalized_phone and len(normalized_phone.lstrip("+")) >= 8:
    safe_phone = html.escape(normalized_phone, quote=True)
    st.markdown(
        f'<a class="emergency-link blue-link" href="tel:{safe_phone}">'
        '📱 보호자에게 전화하기</a>',
        unsafe_allow_html=True,
    )
else:
    st.info("보호자 전화 연결을 사용하려면 연락처를 입력해 주세요.")

# ---------------------------------------
# 신고 기록
# ---------------------------------------
st.markdown('<div class="section-title">📝 최근 신고 기록</div>',
            unsafe_allow_html=True)

if not st.session_state.reports:
    st.markdown(
        '<div class="info-card">아직 기록된 신고 요청이 없습니다.</div>',
        unsafe_allow_html=True,
    )
else:
    for item in st.session_state.reports[:10]:
        with st.expander(
            f"{item['time']} · {item['reason']}"
        ):
            st.write(f"**위치:** {item['location']}")
            st.write(f"**설명:** {item['detail']}")
            st.caption(
                "앱 내부 기록입니다. 119 또는 보호자에게 "
                "자동으로 전송된 기록이 아닙니다."
            )

# ---------------------------------------
# 안내
# ---------------------------------------
st.markdown("---")
st.markdown("""
<div class="small-note">
<b>이용 안내</b><br>
• 이 버전은 앱 화면 안에 신고 요청을 기록하는 시제품입니다.<br>
• 앱을 닫거나 세션이 초기화되면 기록이 사라질 수 있습니다.<br>
• 위치 자동 감지, 낙상 감지, 문자 자동 발송, 119 자동 신고는 구현되어 있지 않습니다.<br>
• 실제 서비스에서는 보호자 수신 서버, 위치 권한, 센서 연동,
  개인정보 보호 및 오신고 방지 절차를 추가해야 합니다.
</div>
""", unsafe_allow_html=True)

