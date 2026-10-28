from datetime import datetime
import os
import time
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS (접근성 및 중앙 SOS 버튼 스타일링)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="거동불편 장애인 위험시 자동신고 시스템",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 고대비 및 대형 버튼 접근성 CSS 적용
st.markdown(
    """
    <style>
    /* 메인 배경 및 타이틀 스타일 */
    .main-title {
        text-align: center;
        color: #d9534f;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #555555;
        font-size: 1.1rem;
        margin-bottom: 25px;
    }
    /* 중앙 SOS 박스 스타일 */
    .sos-container {
        background-color: #fff0f0;
        border: 3px solid #ff4d4d;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0px 10px 20px rgba(255, 77, 77, 0.2);
        margin-bottom: 30px;
    }
    /* 상태 카드 스타일 */
    .status-card {
        background-color: #f8f9fa;
        border-left: 6px solid #0d6efd;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    .alert-card {
        background-color: #fff3cd;
        border-left: 6px solid #ffc107;
        padding: 15px;
        border-radius: 8px;
    }
    .danger-card {
        background-color: #f8d7da;
        border-left: 6px solid #dc3545;
        padding: 15px;
        border-radius: 8px;
    }
    </style>
""",
    unsafe_allow_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. Session State Initialization (상태 관리)
# -----------------------------------------------------------------------------
if "report_logs" not in st.session_state:
  st.session_state.report_logs = []

if "active_emergency" not in st.session_state:
  st.session_state.active_emergency = None


# -----------------------------------------------------------------------------
# 3. Helper Functions & Gemini API Integration
# -----------------------------------------------------------------------------
def get_gemini_api_key():
  """Streamlit Secrets 또는 환경 변수에서 API Key 가져오기"""
  if "GEMINI_API_KEY" in st.secrets:
    return st.secrets["GEMINI_API_KEY"]
  return os.environ.get("GEMINI_API_KEY", None)


def generate_ai_emergency_report(
    user_info, event_type, location_str, sensor_info
):
  """Gemini 2.5 Flash Lite 모델을 활용한 AI 긴급 출동 브리핑 생성"""
  api_key = get_gemini_api_key()

  # API 키가 없는 경우 사용될 기본 브리핑 템플릿
  fallback_report = f"""[119 긴급 출동 요청 - {event_type}]

📍 위치: {location_str}
👤 환자: {user_info['name']} ({user_info['age']}세 / {user_info['gender']})
♿ 장애 정보: {user_info['disability']} (자가 이동 불가)
💊 기저질환: {user_info['conditions']}
📊 센서 감지: {sensor_info}

[구급대원 핵심 주의사항]
• 환자는 거동이 불가능하므로 이송 장비(들것/휠체어) 준비가 필요합니다.
• 현장 거주지 접근 시 엘리베이터 수동 조작 및 비상키 확인이 필요할 수 있습니다.
• 등록된 보호자({user_info['guardian_phone']})에게 자동 비상 알림 메시지가 발송되었습니다.
"""

  if not api_key:
    return fallback_report

  try:
    from google import genai

    client = genai.Client(api_key=api_key)

    prompt = f"""
        너는 거동이 불편한 중증 장애인을 위한 긴급 구조 지원 AI 분석 시스템이야.
        다음 발생 상황과 환자 신상 정보를 바탕으로, 119 상황실 및 현장 출동 구급대원이 즉시 파악해야 하는 '긴급 현장 출동 브리핑 보고서'를 작성해줘.

        [환자 및 현장 정보]
        - 환자 성명: {user_info['name']}
        - 연령/성별: {user_info['age']}세 / {user_info['gender']}
        - 장애 유형 및 상태: {user_info['disability']}
        - 기저질환 및 주요 특이사항: {user_info['conditions']}
        - 주거/발생 위치: {location_str}
        - 비상 연락처: {user_info['guardian_phone']}
        - 발생 이벤트: {event_type}
        - 가상 센서 데이터: {sensor_info}

        [작성 지침]
        1. 첫 줄은 "[119 긴급 출동 요청 - {event_type}]"으로 시작해줘.
        2. 환자의 거동 상태(휠체어 탑승 여부, 진입 장애요인 등)를 구급대원이 바로 파악할 수 있도록 명확히 기술해줘.
        3. 구급대원이 현장에 도착 시 꼭 알아야 할 핵심 진입 및 이송 가이드 3가지를 불렛포인트(•)로 정돈해줘.
        4. 신속한 독해를 위해 명확하고 간결한 한국어로 작성해줘.
        """

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", contents=prompt
    )
    return response.text if response.text else fallback_report

  except Exception as e:
    st.warning(
      f"⚠️ AI 보고서 생성 중 오류가 발생하여 표준 템플릿으로 대체되었습니다. ({e})"
    )
    return fallback_report


def trigger_emergency(event_type, sensor_info, user_info, lat, lon):
  """긴급 신고 발생 처리 함수"""
  now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  location_str = f"서울특별시 마포구 월드컵북로 100 (가상위치: {lat:.4f}, {lon:.4f})"

  # AI 보고서 생성
  ai_report = generate_ai_emergency_report(
      user_info, event_type, location_str, sensor_info
  )

  new_event = {
      "id": len(st.session_state.report_logs) + 1,
      "time": now_str,
      "event_type": event_type,
      "user_name": user_info["name"],
      "sensor_info": sensor_info,
      "location": location_str,
      "lat": lat,
      "lon": lon,
      "report": ai_report,
      "status": "접수 완료 (119 및 보호자 통보됨)",
  }

  st.session_state.active_emergency = new_event
  st.session_state.report_logs.insert(0, new_event)


# -----------------------------------------------------------------------------
# 4. Sidebar: 환자 프로필 & 가상 센서 설정
# -----------------------------------------------------------------------------
st.sidebar.title("⚙️ 사용자 프로필 및 센서 설정")

st.sidebar.subheader("👤 대상자 프로필")
user_name = st.sidebar.text_input("이름", value="홍길동")
user_age = st.sidebar.number_input("나이", value=68, min_value=1, max_value=120)
user_gender = st.sidebar.selectbox("성별", ["남성", "여성"])
user_disability = st.sidebar.selectbox(
    "장애 유형",
    [
        "지체장애 1급 (전동휠체어 사용, 자가 거동 불가)",
        "뇌병변장애 (상지/하무 기능 저하, 언어 장애 소견)",
        "시각/중증 복합장애 (도움 없이 이동 불가)",
        "고령 중증 거동불편 (침상 생활 중)",
    ],
)
user_conditions = st.sidebar.text_area(
    "기저질환 및 참고사항", value="고혈압, 당뇨 약 복용 중. 엘리베이터 탑승 필수."
)
guardian_phone = st.sidebar.text_input(
    "보호자 비상연락처", value="010-1234-5678 (자녀)"
)

user_info = {
    "name": user_name,
    "age": user_age,
    "gender": user_gender,
    "disability": user_disability,
    "conditions": user_conditions,
    "guardian_phone": guardian_phone,
}

st.sidebar.markdown("---")
st.sidebar.subheader("📍 가상 위치 (GPS Coordinates)")
lat = st.sidebar.number_input(
    "위도 (Latitude)", value=37.5665, format="%.4f"
)
lon = st.sidebar.number_input(
    "경도 (Longitude)", value=126.9780, format="%.4f"
)

st.sidebar.markdown("---")
st.sidebar.caption("🚨 본 시스템은 가상 신고 시뮬레이터입니다.")


# -----------------------------------------------------------------------------
# 5. Main UI Header
# -----------------------------------------------------------------------------
st.markdown(
    '<h1 class="main-title">🚨 거동불편 장애인을 위한 위험시 자동신고 시스템</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="sub-title">스마트 센서 감지 및 원터치 버튼을 통한 119 구급대·보호자 AI 자동 신고 시뮬레이션</p>',
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 6. Central Emergency Report Area (요청사항: 중앙에 신고 버튼 배치)
# -----------------------------------------------------------------------------
st.markdown('<div class="sos-container">', unsafe_allow_html=True)
st.markdown(
    "<h2 style='color: #cc0000; margin-top: 0;'>비상 상황 시 아래 버튼을 누르세요</h2>",
    unsafe_allow_html=True,
)

# 컬럼 레이아웃을 통해 버튼을 화면 중앙에 커다랗게 배치
col_l, col_center, col_r = st.columns([1, 2, 1])

with col_center:
  # 원터치 긴급 신고 메인 대형 버튼
  sos_clicked = st.button(
      "🚨 [원터치] 즉시 긴급 신고하기",
      type="primary",
      use_container_width=True,
      help="누르는 즉시 119 및 등록된 보호자에게 AI 브리핑이 자동 전송됩니다.",
  )

st.markdown(
    "<p style='color: #666; margin-top: 15px;'><b>또는 가상 자동감지 시뮬레이션을 테스트해보세요:</b></p>",
    unsafe_allow_html=True,
)

btn_col1, btn_col2, btn_col3 = st.columns(3)

with btn_col1:
  fall_sim = st.button(
      "💥 [자동감지] 낙상 충격 감지", use_container_width=True
  )
with btn_col2:
  heart_sim = st.button(
      "💓 [자동감지] 이상 심박수 감지", use_container_width=True
  )
with btn_col3:
  inact_sim = st.button(
      "⏳ [자동감지] 30분 미동 감지", use_container_width=True
  )

st.markdown("</div>", unsafe_allow_html=True)


# Button Trigger Events Handling
if sos_clicked:
  trigger_emergency(
      "사용자 직접 SOS 긴급신고",
      "원터치 비상버튼 입력됨",
      user_info,
      lat,
      lon,
  )
  st.rerun()

if fall_sim:
  trigger_emergency(
      "낙상 사고 감지",
      "가속도 센서 4.2G 충격 감지 및 바닥 수평 상태 유지",
      user_info,
      lat,
      lon,
  )
  st.rerun()

if heart_sim:
  trigger_emergency(
      "심박수 이상 감지",
      "스마트밴드 측정 심박수 145 bpm 급증 (비상임계치 초과)",
      user_info,
      lat,
      lon,
  )
  st.rerun()

if inact_sim:
  trigger_emergency(
      "장시간 무활동 감지",
      "재실 센서 30분간 호흡 외 자발적 움직임 없음 감지",
      user_info,
      lat,
      lon,
  )
  st.rerun()


# -----------------------------------------------------------------------------
# 7. Active Emergency Status Display (신고 발생 시 활성화)
# -----------------------------------------------------------------------------
if st.session_state.active_emergency:
  active = st.session_state.active_emergency

  st.error("🚨 **[긴급 상황 발생] 신고가 접수되어 구급 및 보호자 통보가 진행 중입니다!**")

  # 취소 및 상황 해제 버튼
  cancel_col1, cancel_col2 = st.columns([3, 1])
  with cancel_col2:
    if st.button("❌ 오작동 / 상황 해제", type="secondary"):
      st.session_state.active_emergency = None
      st.success("신고 상황이 해제되었습니다.")
      st.rerun()

  # 2개의 메인 탭으로 디스플레이
  detail_tab1, detail_tab2 = st.tabs(
      ["🤖 AI 구급 출동 브리핑", "📍 현장 위치 및 라이브 모니터링"]
  )

  with detail_tab1:
    st.subheader("🤖 AI 기반 119 구급대 맞춤 브리핑 보고서 (Gemini 2.5 Flash Lite)")
    st.info(f"⏰ **신고 접수 일시**: {active['time']}")
    st.text_area(
        "생성된 긴급 보고서 내용 (119 전송용)",
        value=active["report"],
        height=220,
    )

    st.subheader("📲 자동 통보 전송 현황")
    st.success(
        f"✅ **119 종합상황실**: 전자 긴급구조 데이터 수신 완료\n\n"
        f"✅ **보호자 알림 ({active['user_name']} 님의 보호자)**: "
        f"SMS 및 자동음성 안내 수신 완료 ('{active['event_type']}' 발생)"
    )

  with detail_tab2:
    st.subheader("📍 가상 발생 위치 지도")
    map_data = pd.DataFrame({"lat": [active["lat"]], "lon": [active["lon"]]})
    st.map(map_data, zoom=14)

    st.subheader("⏱️ 가상 대응 프로세스 단계")
    status_progress = st.progress(60)
    st.caption("현재 단계: [3단계] 119 구급대 출동 지정 및 경로 안내 중...")

st.markdown("---")


# -----------------------------------------------------------------------------
# 8. Logs & System Info Tabs
# -----------------------------------------------------------------------------
tab_log, tab_sensor, tab_info = st.tabs(
    ["📜 긴급 신고 이력 로그", "📊 가상 센서 상태", "ℹ️ 시스템 안내"]
)

with tab_log:
  st.subheader("📋 가상 신고 이력")
  if st.session_state.report_logs:
    df_logs = pd.DataFrame(st.session_state.report_logs)
    st.dataframe(
        df_logs[["id", "time", "event_type", "user_name", "sensor_info", "status"]],
        use_container_width=True,
    )

    # Log Download Button
    csv = df_logs.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 신고 이력 CSV 다운로드",
        data=csv,
        file_name=f'emergency_logs_{datetime.now().strftime("%Y%m%m")}.csv',
        mime="text/csv",
    )
  else:
    st.write("현재까지 등록된 긴급 신고 이력이 없습니다.")

with tab_sensor:
  st.subheader("📡 모니터링 가상 센서 상태")
  s_col1, s_col2, s_col3 = st.columns(3)
  with s_col1:
    st.metric(label="낙상 감지 센서", value="정상", delta
