import streamlit as st
import random
from datetime import datetime

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
# 디자인
# ---------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #f4f8ff 0%, #ffffff 65%);
    }

    .hero {
        text-align: center;
        padding: 22px 8px 8px 8px;
    }

    .brand {
        display: inline-block;
        background: #e4edff;
        color: #204fbd;
        padding: 7px 14px;
        border-radius: 30px;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .hero h1 {
        font-size: 34px;
        font-weight: 900;
        color: #14213d;
        margin: 4px 0 10px 0;
    }

    .hero p {
        color: #596579;
        font-size: 15px;
        line-height: 1.8;
        margin: 0;
    }

    .sos-wrap {
        max-width: 290px;
        margin: 22px auto 18px auto;
        padding: 13px;
        border-radius: 50%;
        background: #ffe4e4;
    }

    .sos-core {
        width: 100%;
        aspect-ratio: 1 / 1;
        border-radius: 50%;
        background: #e52436;
        border: 8px solid #ff6673;
        box-shadow: 0 10px 0 #b7192a, 0 18px 30px #e5243630;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
    }

    .sos-icon {
        font-size: 48px;
        line-height: 1.3;
    }

    .sos-text {
        font-size: 31px;
        font-weight: 900;
        letter-spacing: 2px;
    }

    .sos-sub {
        font-size: 13px;
        margin-top: 5px;
    }

    .stButton > button {
        border-radius: 14px;
        min-height: 48px;
        font-weight: 700;
        width: 100%;
        transition: 0.15s ease;
    }

    div[data-testid="stButton"] button[kind="primary"] {
        background: #e52436;
        border: 1px solid #e52436;
        color: white;
    }

    .info-card {
        padding: 17px;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        background: white;
        margin: 10px 0;
    }

    .info-title {
        color: #17233c;
        font-size: 16px;
        font-weight: 800;
        margin-bottom: 7px;
    }

    .muted {
        color: #667085;
        font-size: 13px;
        line-height: 1.8;
    }

    .footer {
        color: #7b8494;
        text-align: center;
        font-size: 12px;
        line-height: 1.8;
        margin-top: 22px;
        padding: 12px 0;
    }

    @media (max-width: 500px) {
        .hero h1 { font-size: 28px; }
        .sos-wrap { max-width: 250px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------
# 세션 상태 초기화
# ---------------------------------------
if "report" not in st.session_state:
    st.session_state.report = None

if "report_count" not in st.session_state:
    st.session_state.report_count = 0

# ---------------------------------------
# 헤더
# ---------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="brand">🛡️ 장애인 안전 지원 서비스</div>
        <h1>위험할 땐, 안심벨</h1>
        <p>
            도움이 필요한 순간,<br>
            아래의 긴급 신고 버튼을 눌러주세요.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------
# 도움 요청 유형
# ---------------------------------------
st.markdown("### 🙋 어떤 도움이 필요하신가요?")

support_type = st.selectbox(
    "지원 유형 선택",
    [
        "긴급 안전 확인",
        "이동 및 신체 활동 지원",
        "청각 관련 의사소통 지원",
        "시각 관련 이동 안내 지원",
        "의사소통 및 기타 지원",
    ],
    label_visibility="collapsed",
)

# ---------------------------------------
# 중앙 신고 버튼
# ---------------------------------------
st.markdown(
    """
    <div class="sos-wrap">
        <div class="sos-core">
            <div class="sos-icon">🆘</div>
            <div class="sos-text">SOS</div>
            <div class="sos-sub">긴급 도움 요청</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='text-align:center;color:#596579;font-size:14px;'>"
    "위험하거나 도움이 필요하면 아래 버튼을 누르세요.</p>",
    unsafe_allow_html=True,
)

# 실제 동작하는 버튼
if st.session_state.report is None:
    if st.button(
        "🆘  긴급 신고 시뮬레이션 시작",
        type="primary",
        use_container_width=True,
    ):
        try:
            now = datetime.now().astimezone()
            report_id = (
                "SAFE-"
                + now.strftime("%Y%m%d-%H%M%S")
                + "-"
                + str(random.randint(100, 999))
            )

            st.session_state.report = {
                "id": report_id,
                "time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "support": support_type,
            }
            st.session_state.report_count += 1
            st.rerun()
        except Exception:
            st.error("신고 시뮬레이션을 시작하지 못했습니다. 다시 시도해주세요.")
else:
    report = st.session_state.report

    st.success("✅ 가상 신고가 정상적으로 접수되었습니다!")

    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-title">📋 신고 접수 확인서</div>
            <p><b>접수 번호</b><br>{report["id"]}</p>
            <p><b>접수 시간</b><br>{report["time"]}</p>
            <p><b>요청 지원</b><br>{report["support"]}</p>
            <p><b>처리 상태</b><br>가상 접수 완료 · 실제 출동 요청 없음</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "이 접수는 화면 시연용입니다. 경찰·소방 기관이나 "
        "보호자에게 신고가 전달되지 않았습니다."
    )

    if st.button("↩️ 신고 취소 및 처음으로 돌아가기"):
        st.session_state.report = None
        st.rerun()

# ---------------------------------------
# 안전 정보
# ---------------------------------------
st.markdown("---")
st.markdown("### 📞 실제 긴급 상황이라면")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-title">🚓 경찰 신고</div>
            <div style="font-size:28px;font-weight:900;color:#204fbd;">
                112
            </div>
            <div class="muted">범죄, 폭력, 신변 위협 등</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="info-card">
            <div class="info-title">🚒 구급·소방</div>
            <div style="font-size:28px;font-weight:900;color:#e52436;">
                119
            </div>
            <div class="muted">응급환자, 화재, 구조 요청 등</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.info(
    "사용이 어려운 상황이라면 주변 사람에게 도움을 요청하거나 "
    "본인이 이용할 수 있는 긴급 연락 수단을 사용하세요. "
    "이 웹 앱은 실제 긴급 신고를 대신하지 않습니다."
)

st.markdown(
    f"""
    <div class="footer">
        안심벨 · 장애인 안전 지원 프로토타입<br>
        현재 브라우저 세션의 가상 신고 횟수: {st.session_state.report_count}<br>
        실제 위치 추적 및 외부 신고 전송 기능은 제공하지 않습니다.
    </div>
    """,
    unsafe_allow_html=True,
)

.sos-wrap {
    max-width: 290px;
    margin: 28px auto;
    padding: 14px;
    border-radius: 50%;
    background: #ffe4e4;
    animation: halo 1.8s infinite;
}

.sos-core {
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 50%;
    background: linear-gradient(145deg, #ff4757, #c90020);
    border: 8px solid #ff8791;
    box-shadow: 0 9px 0 #a91525,
                0 15px 30px #e5243655;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: white;
    cursor: pointer;
    transition: transform 0.15s ease;
}

.sos-core:hover {
    transform: scale(1.04);
}

.sos-core:active {
    transform: scale(0.94);
}

.sos-icon {
    font-size: 52px;
    line-height: 1.3;
    animation: heartbeat 1.1s infinite;
}

.sos-text {
    font-size: 36px;
    font-weight: 900;
    letter-spacing: 3px;
}

.sos-sub {
    font-size: 13px;
    margin-top: 5px;
    font-weight: 700;
}

@keyframes heartbeat {
    0%, 100% { transform: scale(1); }
    15% { transform: scale(1.18); }
    30% { transform: scale(1); }
    45% { transform: scale(1.12); }
}

@keyframes halo {
    0% { box-shadow: 0 0 0 0 #ff526655; }
    70% { box-shadow: 0 0 0 16px #ff526600; }
    100% { box-shadow: 0 0 0 0 #ff526600; }
}

.sos-wrap {
    max-width: 290px;
    margin: 28px auto;
    padding: 14px;
    border-radius: 50%;
    background: #ffe4e4;
    animation: halo 1.8s infinite;
}

.sos-core {
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 50%;
    background: linear-gradient(145deg, #ff4757, #c90020);
    border: 8px solid #ff8791;
    box-shadow: 0 9px 0 #a91525,
                0 15px 30px #e5243655;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: white;
    cursor: pointer;
    transition: transform 0.15s ease;
}

.sos-core:hover {
    transform: scale(1.04);
}

.sos-core:active {
    transform: scale(0.94);
}

.sos-icon {
    font-size: 52px;
    line-height: 1.3;
    animation: heartbeat 1.1s infinite;
}

.sos-text {
    font-size: 36px;
    font-weight: 900;
    letter-spacing: 3px;
}

.sos-sub {
    font-size: 13px;
    margin-top: 5px;
    font-weight: 700;
}

@keyframes heartbeat {
    0%, 100% { transform: scale(1); }
    15% { transform: scale(1.18); }
    30% { transform: scale(1); }
    45% { transform: scale(1.12); }
}

@keyframes halo {
    0% { box-shadow: 0 0 0 0 #ff526655; }
    70% { box-shadow: 0 0 0 16px #ff526600; }
    100% { box-shadow: 0 0 0 0 #ff526600; }
}

.sos-wrap {
    max-width: 290px;
    margin: 28px auto;
    padding: 14px;
    border-radius: 50%;
    background: #ffe4e4;
    animation: halo 1.8s infinite;
}

.sos-core {
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 50%;
    background: linear-gradient(145deg, #ff4757, #c90020);
    border: 8px solid #ff8791;
    box-shadow: 0 9px 0 #a91525,
                0 15px 30px #e5243655;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: white;
    cursor: pointer;
    transition: transform 0.15s ease;
}

.sos-core:hover {
    transform: scale(1.04);
}

.sos-core:active {
    transform: scale(0.94);
}

.sos-icon {
    font-size: 52px;
    line-height: 1.3;
    animation: heartbeat 1.1s infinite;
}

.sos-text {
    font-size: 36px;
    font-weight: 900;
    letter-spacing: 3px;
}

.sos-sub {
    font-size: 13px;
    margin-top: 5px;
    font-weight: 700;
}

@keyframes heartbeat {
    0%, 100% { transform: scale(1); }
    15% { transform: scale(1.18); }
    30% { transform: scale(1); }
    45% { transform: scale(1.12); }
}

@keyframes halo {
    0% { box-shadow: 0 0 0 0 #ff526655; }
    70% { box-shadow: 0 0 0 16px #ff526600; }
    100% { box-shadow: 0 0 0 0 #ff526600; }
}
