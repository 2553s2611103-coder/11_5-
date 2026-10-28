import random
from datetime import datetime

import streamlit as st

try:
    from streamlit_geolocation import streamlit_geolocation
except Exception:
    streamlit_geolocation = None


st.set_page_config(
    page_title="함께가는 버스",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- 디자인 ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .stApp { background: #f4f8ff; }
    .block-container { max-width: 1120px; padding-top: 1.5rem; padding-bottom: 3rem; }
    .hero {
        background: linear-gradient(125deg, #e5f1ff 0%, #f8fbff 75%);
        border: 1px solid #dceaff; border-radius: 24px; padding: 26px 28px;
        margin-bottom: 18px;
    }
    .brand { color: #2673e8; font-size: 15px; font-weight: 800; letter-spacing: -.2px; }
    .hero h1 { color: #122a59; font-size: clamp(27px, 4vw, 38px); line-height: 1.25; margin: 12px 0 10px; }
    .hero p { color: #526789; font-size: 15px; margin: 0; }
    .panel {
        background: white; border: 1px solid #e1eaf7; border-radius: 20px;
        padding: 20px; margin-bottom: 16px;
    }
    .section-title { color: #173361; font-weight: 800; font-size: 19px; margin-bottom: 8px; }
    .muted { color: #667995; font-size: 13px; }
    .step {
        background: white; border: 1px solid #e2ebf8; border-radius: 14px;
        padding: 12px 8px; text-align: center; color: #355078; font-size: 12px;
    }
    .step-active { border: 2px solid #3981ef; background: #edf5ff; color: #1559bd; font-weight: 800; }
    .big-number { font-size: 27px; font-weight: 800; color: #1e66d1; }
    div.stButton > button[kind="primary"] {
        background: #2673e8; border: 0; border-radius: 12px; min-height: 48px; font-weight: 800;
    }
    div.stButton > button { border-radius: 11px; }
    [data-testid="stMetric"] { background: #f4f8ff; border-radius: 14px; padding: 12px; }
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

VEHICLES = {
    "휠체어 리프트 차량": {
        "icon": "♿",
        "description": "휠체어 고정 장치와 승강 장치가 필요한 이용자",
        "eta": (8, 18),
    },
    "저상형 이동 차량": {
        "icon": "🚌",
        "description": "높은 계단 없이 편하게 승하차하고 싶은 이용자",
        "eta": (6, 15),
    },
    "동행 지원 차량": {
        "icon": "🤝",
        "description": "승하차 시 동행인의 도움이 필요한 이용자",
        "eta": (10, 22),
    },
}

if "ride" not in st.session_state:
    st.session_state.ride = None
if "ride_status" not in st.session_state:
    st.session_state.ride_status = "대기"
if "ride_history" not in st.session_state:
    st.session_state.ride_history = []


def valid_coordinates(value):
    """위치 컴포넌트의 결과가 유효한 위도/경도인지 확인."""
    if not isinstance(value, dict):
        return False
    try:
        lat = float(value.get("latitude"))
        lon = float(value.get("longitude"))
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except (TypeError, ValueError):
        return False


# ---------- 상단 소개 ----------
st.markdown(
    """
    <div class="hero">
      <div class="brand">🚌 함께가는 버스</div>
      <h1>움직이기 힘든 당신을 위한<br>맞춤형 대중교통</h1>
      <p>지금 있는 곳에서 목적지까지, 필요한 이동 지원을 간편하게 요청하세요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 단계 표시
status_to_step = {
    "대기": 1,
    "호출 완료": 2,
    "차량 출발": 3,
    "차량 도착": 3,
    "탑승 완료": 4,
    "이용 완료": 5,
}
current_step = status_to_step.get(st.session_state.ride_status, 1)
steps = ["위치 확인", "차량 호출", "도착 알림", "안전한 탑승", "목적지 도착"]
step_cols = st.columns(5)
for idx, (col, label) in enumerate(zip(step_cols, steps), start=1):
    with col:
        css_class = "step step-active" if idx == current_step else "step"
        st.markdown(
            f'<div class="{css_class}"><b>{idx}</b><br>{label}</div>',
            unsafe_allow_html=True,
        )

left, right = st.columns([1.12, 0.88], gap="large")

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📍 현재 위치 확인</div>', unsafe_allow_html=True)
    st.caption("위치 정보는 이 화면에서 차량 호출 정보를 만드는 데 사용됩니다.")

    location_data = None
    if streamlit_geolocation is not None:
        try:
            location_data = streamlit_geolocation()
        except Exception:
            location_data = None
    else:
        st.info("자동 위치 확인 기능을 불러오지 못했습니다. 아래에서 출발지를 직접 입력해 주세요.")

    has_gps = valid_coordinates(location_data)
    if has_gps:
        lat = float(location_data["latitude"])
        lon = float(location_data["longitude"])
        st.success("현재 위치를 확인했어요.")
        st.code(f"위도 {lat:.5f} · 경도 {lon:.5f}", language=None)
        if st.button("지도에서 현재 위치 열기", use_container_width=True):
            st.link_button(
                "Google 지도에서 위치 보기",
                f"https://www.google.com/maps?q={lat},{lon}",
                use_container_width=True,
            )
    else:
        st.info("위치 확인 버튼을 누르고 브라우저의 위치 권한을 허용해 주세요. 사용하지 않으려면 주소를 직접 입력할 수 있어요.")

    with st.form("ride_request_form"):
        start_default = ""
        start_location = st.text_input(
            "출발지",
            value=start_default,
            placeholder="예: 서울시 마포구 월드컵북로 00",
            help="GPS를 확인했더라도 정확한 승차 장소를 주소나 건물명으로 적어 주세요.",
        )
        destination = st.text_input(
            "목적지",
            placeholder="예: 서울아산병원 정문",
        )
        vehicle_type = st.radio(
            "원하는 차량 유형",
            list(VEHICLES.keys()),
            horizontal=False,
            format_func=lambda item: f'{VEHICLES[item]["icon"]}  {item} — {VEHICLES[item]["description"]}',
        )
        extra_help = st.selectbox(
            "추가 지원 사항",
            ["특별한 요청 없음", "휠체어 고정 및 리프트 지원", "승하차 시 도움 필요", "보호자와 함께 탑승"],
        )
        submitted = st.form_submit_button("🚌  대중교통 호출하기", type="primary", use_container_width=True)

    if submitted:
        if not start_location.strip() and not has_gps:
            st.error("출발지를 입력하거나 현재 위치를 확인해 주세요.")
        elif not destination.strip():
            st.error("목적지를 입력해 주세요.")
        else:
            low, high = VEHICLES[vehicle_type]["eta"]
            eta = random.randint(low, high)
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.session_state.ride = {
                "start": start_location.strip() or f"현재 위치 ({float(location_data['latitude']):.5f}, {float(location_data['longitude']):.5f})",
                "destination": destination.strip(),
                "vehicle": vehicle_type,
                "help": extra_help,
                "eta": eta,
                "vehicle_number": f"함께 {random.randint(100, 999)}호",
                "requested_at": now,
            }
            st.session_state.ride_status = "호출 완료"
            st.session_state.ride_history.append({
                "요청 시각": now,
                "출발지": st.session_state.ride["start"],
                "목적지": destination.strip(),
                "차량": vehicle_type,
                "상태": "호출 완료",
            })
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚐 이용 안내</div>', unsafe_allow_html=True)
    st.markdown(
        """
        **누구나 편리하게 이동할 수 있도록**

        - ♿ 휠체어 이용에 적합한 차량 유형 선택
        - 📍 출발 위치와 목적지를 한 화면에서 입력
        - ⏱️ 호출 이후 예상 대기 시간 확인
        - 🛡️ 단계별 탑승 상태 확인
        """
    )
    st.markdown("---")
    st.markdown("**호출 진행 순서**")
    st.markdown("1. 출발지와 목적지를 입력해요.")
    st.markdown("2. 필요한 차량과 지원 유형을 선택해요.")
    st.markdown("3. 호출 후 차량 상태를 단계별로 변경해요.")
    st.caption("※ 이 앱은 시연용 프로토타입이며 실제 차량을 배차하거나 긴급 이동을 지원하지 않습니다.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- 호출 후 진행 상태 ----------
ride = st.session_state.ride
if ride:
    st.markdown("## 🚦 내 이동 현황")
    status = st.session_state.ride_status
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(f"### {status}")
    info_cols = st.columns(3)
    with info_cols[0]:
        st.metric("예상 대기 시간", f'{ride["eta"]}분' if status in ["호출 완료", "차량 출발"] else ("도착" if status in ["차량 도착", "탑승 완료", "이용 완료"] else "-"))
    with info_cols[1]:
        st.metric("차량 번호", ride["vehicle_number"])
    with info_cols[2]:
        st.metric("선택 차량", ride["vehicle"])

    st.write(f'**출발지:** {ride["start"]}')
    st.write(f'**목적지:** {ride["destination"]}')
    st.write(f'**추가 지원:** {ride["help"]}')

    if status == "호출 완료":
        st.info(f'차량을 배정했어요. 시연용 예상 대기 시간은 약 {ride["eta"]}분입니다.')
        if st.button("차량 출발 처리", type="primary", use_container_width=True):
            st.session_state.ride_status = "차량 출발"
            st.rerun()
    elif status == "차량 출발":
        st.info("차량이 출발했어요. 실제 위치 추적이 아닌 시연용 상태입니다.")
        if st.button("차량 도착 처리", type="primary", use_container_width=True):
            st.session_state.ride_status = "차량 도착"
            st.rerun()
    elif status == "차량 도착":
        st.success("차량이 승차 장소에 도착했어요. 주변을 확인하고 안전하게 탑승해 주세요.")
        if st.button("탑승 완료", type="primary", use_container_width=True):
            st.session_state.ride_status = "탑승 완료"
            st.rerun()
    elif status == "탑승 완료":
        st.info("탑승이 확인됐어요. 목적지에 도착한 뒤 이용을 완료해 주세요.")
        if st.button("목적지 도착 · 이용 완료", type="primary", use_container_width=True):
            st.session_state.ride_status = "이용 완료"
            if st.session_state.ride_history:
                st.session_state.ride_history[-1]["상태"] = "이용 완료"
            st.rerun()
    elif status == "이용 완료":
        st.success("이용이 완료되었습니다. 함께가는 버스를 이용해 주셔서 감사합니다!")
        if st.button("새로운 차량 호출하기", use_container_width=True):
            st.session_state.ride = None
            st.session_state.ride_status = "대기"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- 이용 기록 ----------
with st.expander("🧾 이용 요청 기록"):
    if st.session_state.ride_history:
        st.dataframe(st.session_state.ride_history, use_container_width=True, hide_index=True)
    else:
        st.caption("아직 이용 요청 기록이 없습니다.")

st.markdown(
    """
    <div style="text-align:center;color:#8292aa;font-size:12px;padding:16px 0 0">
    함께가는 버스 · 이동의 자유를 함께 만들어요 💙
    </div>
    """,
    unsafe_allow_html=True,
)
