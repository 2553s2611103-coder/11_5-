from datetime import datetime
import os
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 디자인 (대형 비상 버튼 접근성 강화)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="거동불편 장애인 긴급 자동신고 시스템",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 화면 중앙 대형 버튼 및 비상 스타일 CSS 적용
st.markdown(
    """
    <style>
    .main-header {
        text-align: center;
        color: #d9534f;
        margin-bottom: 5px;
    }
    .sub-header {
        text-align: center;
        color: #666666;
        margin-bottom: 25px;
    }
    .sos-box {
        background-color: #ffeef0;
        border: 3px solid #ff4d4d;
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
""",
    unsafe_allow_allow_html=True,
)

# -----------------------------------------------------------------------------
# 2. 세션 상태 초기화 (신고 이력 및 현재 비상 상태 관리)
# -----------------------------------------------------------------------------
if "report_logs" not in st.session_state:
  st.session_state.report_logs = []

if "current_emergency" not in st.session_state:
  st.session_state.current_emergency = None


# -----------------------------------------------------------------------------
# 3. Gemini AI 함수 및 브리핑 생성 처리
# -----------------------------------------------------------------------------
def get_api_key():
  """Streamlit Secrets 또는 환경 변수에서 Gemini API 키 탐색"""
  if "GEMINI_API_KEY" in st.secrets:
    return st.secrets["GEMINI_API_KEY"]
  return os.environ.get("GEMINI_API_KEY", None)


def generate_emergency_briefing(user_info, event_name, location_str, sensor_data):
  """Gemini 2.5 Flash Lite를 이용한 119 출동 구급대용 브리핑 생성"""
  api_key = get_api_key()

  # 예외 상황 및 API 키 부재 시 사용할 기본 브리핑
  default_report = f"""[119 긴급 출동 요청 - {event_name}]

📍 비상 위치: {location_str}
👤 환자 인적사항: {user_info['name']} ({user_info['age']}세 / {user_info['gender']})
♿ 장애 상태: {user_info['disability']}
💊 기저질환: {user_info['conditions']}
📡 센서 정보: {sensor_data}

[구급대원 사전 준비 사항]
• 환자는 자가 거동이 불가능하므로 이송용 들것 및 전동 휠체어 이동
