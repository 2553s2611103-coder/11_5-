
import streamlit as st
from datetime import datetime
import html
import uuid

# ==========================================
# 1. 기본 설정
# ==========================================
st.set_page_config(
    page_title="안심벨 | 가상 안전 신고",
    page_icon="⚠️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 2. 세션 데이터 초기화
# ==========================================
if "reports" not in st.session_state:
    st.session_state.reports = []

if "last_report_id" not in st.session_state:
    st.session_state.last_report_id = None

if "demo_message" not in st.session_state:
    st.session_state.demo_message = ""

# ==========================================
# 3. 디자인
# ==========================================
st.markdown("""
<style>
@import url(
'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap'
);

.stApp {
    background: linear-gradient(
        180deg,
        #eaf2ff 0%,
        #f7f9ff 36%,
        #ffffff 100%
    );
    font-family: 'Noto Sans KR', sans-serif;
}

.block-container {
    max-width: 760px;
    padding: 25px 18px 45px;
}

.brand {
    display: inline-block;
    padding: 8px 15px;
    border-radius: 30px;
    background: #dce8ff;
    color: #214eae;
    font-weight: 900;
    font-size: 14px;
    letter-spacing: 0.5px;
}

.hero {
    text-align: center;
    padding: 20px 5px 15px;
}

.hero-icon {
    font-size: 46px;
    margin-bottom: 5px;
}

.hero h1 {
    color: #16366f;
    font-size: clamp(28px, 5vw, 38px);
    font-weight: 900;
    margin: 5px 0 12px;
    letter-spacing: -1.2px;
}

.hero p {
    color: #52627b;
    font-size: 16px;
    line-height: 1.9;
    margin: 0;
}

.demo-notice {
    padding: 13px 16px;
    background: #fff5d8;
    border: 1px solid #f2d68c;
    border-radius: 14px;
    color: #78550b;
    font-size: 14px;
    line-height: 1.8;
    margin: 10px 0 20px;
}

.panel {
    background: rgba(255,255,255,0.92);
    border: 1px solid #dfe8f7;
    border-radius: 20px;
    padding: 18px;
    margin: 12px 0;
    box-shadow: 0 5px 20px rgba(37, 71, 130, 0.045);
}

.section-heading {
    color: #19396f;
    font-size: 20px;
    font-weight: 900;
    margin: 22px 0 10px;
}

div[data-testid="stRadio"] label {
    font-size: 16px;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    border-radius: 12px;
    border-color: #cbd9ed;
}

/* 원형 SOS 버튼 */
div.stButton {
    display: flex;
    justify-content: center;
    width: 100%;
}

div.stButton > button[kind="primary"] {
    width: 154px !important;
    min-width: 154px !important;
    height: 154px !important;
    min-height: 154px !important;
    padding: 0 !important;
    margin: 18px auto 15px !important;

    border: 8px solid #ffffff !important;
    outline: 2px solid #d6c9a6 !important;
    border-radius: 50% !important;

    background: radial-gradient(
        ellipse at 34% 21%,
        #ff8872 0%,
        #fa3d28 27%,
        #e52216 59%,
        #bd140d 100%
    ) !important;

    color: #ffffff !important;
    font-size: 27px !important;
    font-weight: 900 !important;
    letter-spacing: 1px !important;

    box-shadow:
        0 8px 0 #97180f,
        0 13px 20px rgba(42, 49, 69, 0.24),
        inset 0 3px 5px rgba(255,255,255,0.58) !important;

    transition:
        transform 0.16s ease,
        box-shadow 0.16s ease,
        filter 0.16s ease !important;
}

div.stButton > button[kind="primary"]:hover {
    transform: translateY(-3px) scale(1.035) !important;
    filter: brightness(1.05);
    box-shadow:
        0 11px 0 #97180f,
        0 17px 24px rgba(42, 49, 69, 0.26),
        inset 0 3px 5px rgba(255,255,255,0.58) !important;
}

div.stButton > button[kind="primary"]:active {
    transform: translateY(5px) scale(0.98) !important;
    box-shadow:
        0 2px 0 #97180f,
        inset 0 3px 5px rgba(255,255,255,0.4) !important;
}

div.stButton > button:focus-visible {
    outline: 4px solid #2454b8 !important;
    outline-offset: 5px !important;
}

.button-caption {
    text-align: center;
    color: #52627b;
    font-weight: 700;
    font-size: 15px;
    margin: 0 0 14px;
}

.report-card {
    background: #f0f7ff;
    border: 1px solid #d2e4ff;
    border-radius: 16px;
    padding: 17px;
    color: #213d6a;
    line-height: 1.9;
    overflow-wrap: anywhere;
}

.status-pill {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: #dff5e7;
    color: #176d3b;
    font-size: 12px;
    font-weight: 900;
}

.footer {
    text-align: center;
    color: #6c7b92;
    font-size: 13px;
    line-height: 1.9;
    padding-top: 18px;
}

@media (prefers-reduced-motion: reduce) {
    div.stButton > button {
        transition: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. 상단 소개
# ==========================================
st.markdown(
    '<div class="brand">🛟 안심벨 SAFETY</div>',
    unsafe_allow_html=True,
)

st.markdown("""
<div class="hero">
    <div class="hero-icon">🛟</div>
    <h1>당신의 안전을 위한 안심벨</h1>
    <p>
        위험 상황을 선택하고 버튼을 눌러 보세요.<br>
        누구나 쉽게 이용할 수 있는 가상 신고 체험입니다.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="demo-notice">
    <b>ℹ️ 가상 신고 전용 앱</b><br>
    이 앱은 시뮬레이션입니다. 실제 112·119 신고,
    전화 연결, 문자 전송 또는 외부 알림은 발생하지 않습니다.
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 위험 상황 선택
# ==========================================
st.markdown(
    '<div class="section-heading">📋 어떤 상황인가요?</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    reason = st.radio(
        "가상 신고 유형",
        [
            "🧍 넘어짐 또는 낙상",
            "♿ 이동하기 어려움",
            "⚠️ 주변의 위협",
            "🆘 기타 긴급 상황",
        ],
        index=0,
    )

    location = st.text_input(
        "현재 위치 (선택)",
        placeholder="예: 집 거실, 건물 2층",
        max_chars=150,
    )

    detail = st.text_area(
        "상황 설명 (선택)",
        placeholder="예: 혼자 움직이기 어려운 상황이에요.",
        max_chars=500,
        height=100,
    )

# ==========================================
# 6. 원형 가상 신고 버튼
# ==========================================
st.markdown(
    '<div class="section-heading">🔴 가상 신고</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="button-caption">'
    '아래 원형 버튼을 눌러 가상 신고를 진행하세요'
    '</div>',
    unsafe_allow_html=True,
)

if st.button(
    "SOS",
    type="primary",
    key="virtual_sos",
    help="실제 신고가 아닌 가상 신고를 접수합니다.",
):
    try:
        report = {
            "id": uuid.uuid4().hex,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reason": reason,
            "location": location.strip() or "위치 미입력",
            "detail": detail.strip() or "추가 설명 없음",
            "status": "가상 접수 완료",
        }

        st.session_state.reports.insert(0, report)
        st.session_state.last_report_id = report["id"]
        st.session_state.demo_message = (
            "가상 신고가 정상적으로 접수되었습니다."
        )

    except Exception:
        st.session_state.demo_message = (
            "가상 신고 처리 중 문제가 발생했습니다. 다시 시도해 주세요."
        )

if st.session_state.demo_message:
    if st.session_state.last_report_id:
        st.success("✅ " + st.session_state.demo_message)
    else:
        st.error(st.session_state.demo_message)

# ==========================================
# 7. 최근 접수 결과
# ==========================================
last_id = st.session_state.last_report_id
latest = next(
    (
        report for report in st.session_state.reports
        if report["id"] == last_id
    ),
    None,
)

if latest:
    st.markdown(
        '<div class="section-heading">✅ 접수 결과</div>',
        unsafe_allow_html=True,
    )

    safe_time = html.escape(latest["time"])
    safe_reason = html.escape(latest["reason"])
    safe_location = html.escape(latest["location"])
    safe_detail = html.escape(latest["detail"])

    st.markdown(f"""
    <div class="report-card">
        <span class="status-pill">가상 접수 완료</span>
        <h3>가상 신고가 기록되었어요.</h3>
        <b>접수 시각</b>: {safe_time}<br>
        <b>신고 유형</b>: {safe_reason}<br>
        <b>현재 위치</b>: {safe_location}<br>
        <b>상황 설명</b>: {safe_detail}<br><br>
        <small>
        이 기록은 현재 앱 세션 안에만 존재하며
        외부 기관이나 다른 사람에게 전달되지 않습니다.
        </small>
    </div>
    """, unsafe_allow_html=True)

    if st.button("↩️ 방금 접수한 가상 신고 취소", key="cancel_latest"):
        st.session_state.reports = [
            report for report in st.session_state.reports
            if report["id"] != last_id
        ]
        st.session_state.last_report_id = None
        st.session_state.demo_message = "가상 신고가 취소되었습니다."
        st.rerun()

# ==========================================
# 8. 신고 기록
# ==========================================
st.markdown(
    '<div class="section-heading">📝 가상 신고 기록</div>',
    unsafe_allow_html=True,
)

reports = st.session_state.reports

if not reports:
    st.info("아직 접수된 가상 신고가 없습니다.")
else:
    st.caption(f"현재 세션의 가상 신고 {len(reports)}건")

    for report in reports[:10]:
        title = f"{report['time']} · {report['reason']}"

        with st.expander(title):
            st.write("**상태:** 가상 접수")
            st.write("**위치:** " + report["location"])
            st.write("**설명:** " + report["detail"])

    if st.button("🗑️ 가상 신고 기록 전체 지우기", key="clear_reports"):
        st.session_state.reports = []
        st.session_state.last_report_id = None
        st.session_state.demo_message = ""
        st.rerun()

# ==========================================
# 9. 하단 안내
# ==========================================
st.markdown("---")

st.markdown("""
<div class="footer">
    <b>안심벨 | 가상 안전 신고 체험</b><br>
    신고 버튼을 눌러도 실제 신고는 접수되지 않습니다.<br>
    기록은 앱 세션이 종료되면 사라질 수 있습니다.
</div>
""", unsafe_allow_html=True)
