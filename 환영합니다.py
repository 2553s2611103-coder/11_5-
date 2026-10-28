import json
import streamlit as st
from streamlit.components.v1 import html as st_html

st.set_page_config(
    page_title="모두의 소리·눈·말 - 장애인 접근성 센터",
    page_icon="♿",
    layout="wide",
)

# ------------------------------------------------------------------
# 세션 상태 초기화
# ------------------------------------------------------------------
if "sentence" not in st.session_state:
    st.session_state.sentence = []
if "custom_phrases" not in st.session_state:
    st.session_state.custom_phrases = []
if "free_in" not in st.session_state:
    st.session_state.free_in = ""

# ------------------------------------------------------------------
# 사이드바: 접근성 설정
# ------------------------------------------------------------------
THEMES = {
    "기본 (밝은 색)": ("#FFFFFF", "#1A1A1A", "#1B5FBF", "#FFFFFF", "#F1F5FB"),
    "고대비 (검정 배경 + 노랑 글자)": ("#000000", "#FFE600", "#FFE600", "#000000", "#1A1A1A"),
    "고대비 (흰 배경 + 검정 글자)": ("#FFFFFF", "#000000", "#000000", "#FFFFFF", "#EDEDED"),
    "눈이 편한 크림색": ("#FFF8E7", "#2B2B2B", "#8A4B00", "#FFFFFF", "#FFEFC8"),
}

with st.sidebar:
    st.header("⚙ 화면 설정")
    font_px = st.slider("글자 크기", 16, 36, 20)
    theme_name = st.radio("화면 색상", list(THEMES.keys()))
    line_h = st.slider("줄 간격", 1.2, 2.2, 1.6, 0.1)
    reduce_motion = st.checkbox("깜빡임·움직임 줄이기", value=False)
    st.caption("키보드 사용 시 Tab 키로 이동, Enter 또는 Space 키로 선택할 수 있어요.")

BG, FG, ACCENT, BTN_FG, CARD = THEMES.get(theme_name, THEMES["기본 (밝은 색)"])

st.markdown(
    f"""
<style>
.stApp {{ background-color: {BG}; color: {FG}; font-size: {font_px}px; line-height: {line_h}; }}
section[data-testid="stSidebar"] > div {{ background-color: {CARD}; }}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp li,
.stApp label, .stApp span, .stApp div[data-testid="stMarkdownContainer"] {{ color: {FG}; }}
.stApp p, .stApp li, .stApp label {{ font-size: {font_px}px; }}
.stApp button {{
    background-color: {ACCENT}; color: {BTN_FG}; border: 3px solid {FG};
    border-radius: 14px; min-height: 3em; font-weight: 700;
}}
.stApp button p {{ color: {BTN_FG} !important; font-size: {font_px}px; font-weight: 700; }}
.stApp button:focus {{ outline: 4px solid #FF6A00; outline-offset: 2px; }}
.stApp textarea, .stApp input {{
    background-color: {CARD} !important; color: {FG} !important;
    font-size: {font_px}px !important; border: 2px solid {FG} !important;
}}
.card {{
    background-color: {CARD}; border: 3px solid {FG}; border-radius: 18px;
    padding: 18px 20px; margin-bottom: 14px;
}}
.bigtext {{
    background-color: {CARD}; border: 3px solid {FG}; border-radius: 18px;
    padding: 20px; font-size: {font_px * 1.8}px; font-weight: 700; line-height: 1.5;
    word-break: keep-all; white-space: pre-wrap;
}}
.braille {{
    background-color: {CARD}; border: 3px solid {FG}; border-radius: 18px;
    padding: 20px; font-size: {font_px * 1.8}px; line-height: 1.9; white-space: pre-wrap;
    word-break: break-all;
}}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# 점자 변환 (한글 점자 - 약자 생략 단순 버전)
# ------------------------------------------------------------------
def dp(pattern: str) -> str:
    """'145' 또는 '6+4' 형식의 점 번호를 유니코드 점자로 변환"""
    result = ""
    for part in pattern.split("+"):
        if part:
            result += chr(0x2800 + sum(1 << (int(c) - 1) for c in part))
    return result


CHO_LIST = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ",
            "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
JUNG_LIST = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ",
             "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
JONG_LIST = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ",
             "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ",
             "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]

CHO_BR = {
    "ㄱ": dp("4"), "ㄴ": dp("14"), "ㄷ": dp("24"), "ㄹ": dp("5"), "ㅁ": dp("15"),
    "ㅂ": dp("45"), "ㅅ": dp("6"), "ㅇ": "", "ㅈ": dp("46"), "ㅊ": dp("56"),
    "ㅋ": dp("124"), "ㅌ": dp("125"), "ㅍ": dp("145"), "ㅎ": dp("245"),
    "ㄲ": dp("6+4"), "ㄸ": dp("6+24"), "ㅃ": dp("6+45"), "ㅆ": dp("6+6"), "ㅉ": dp("6+46"),
}
JUNG_BR = {
    "ㅏ": dp("126"), "ㅑ": dp("345"), "ㅓ": dp("234"), "ㅕ": dp("156"),
    "ㅗ": dp("136"), "ㅛ": dp("346"), "ㅜ": dp("134"), "ㅠ": dp("146"),
    "ㅡ": dp("246"), "ㅣ": dp("135"), "ㅐ": dp("1235"), "ㅔ": dp("1345"),
    "ㅒ": dp("345+1235"), "ㅖ": dp("34"), "ㅘ": dp("12356"),
    "ㅙ": dp("12356+1235"), "ㅚ": dp("13456"), "ㅝ": dp("1234"),
    "ㅞ": dp("1234+1235"), "ㅟ": dp("134+1235"), "ㅢ": dp("2456"),
}
JONG_BR = {
    "": "", "ㄱ": dp("1"), "ㄲ": dp("1+1"), "ㄳ": dp("1+3"), "ㄴ": dp("25"),
    "ㄵ": dp("25+13"), "ㄶ": dp("25+356"), "ㄷ": dp("35"), "ㄹ": dp("2"),
    "ㄺ": dp("2+1"), "ㄻ": dp("2+26"), "ㄼ": dp("2+12"), "ㄽ": dp("2+3"),
    "ㄾ": dp("2+236"), "ㄿ": dp("2+256"), "ㅀ": dp("2+356"), "ㅁ": dp("26"),
    "ㅂ": dp("12"), "ㅄ": dp("12+3"), "ㅅ": dp("3"), "ㅆ": dp("34"),
    "ㅇ": dp("2356"), "ㅈ": dp("13"), "ㅊ": dp("23"), "ㅋ": dp("235"),
    "ㅌ": dp("236"), "ㅍ": dp("256"), "ㅎ": dp("356"),
}
LATIN_BR = {
    "a": "1", "b": "12", "c": "14", "d": "145", "e": "15", "f": "124", "g": "1245",
    "h": "125", "i": "24", "j": "245", "k": "13", "l": "123", "m": "134", "n": "1345",
    "o": "135", "p": "1234", "q": "12345", "r": "1235", "s": "234", "t": "2345",
    "u": "136", "v": "1236", "w": "2456", "x": "1346", "y": "13456", "z": "1356",
}
LATIN_BR = {k: dp(v) for k, v in LATIN_BR.items()}
DIGIT_BR = {
    "1": dp("1"), "2": dp("12"), "3": dp("14"), "4": dp("145"), "5": dp("15"),
    "6": dp("124"), "7": dp("1245"), "8": dp("125"), "9": dp("24"), "0": dp("245"),
}
NUM_SIGN = dp("3456")
PUNCT_BR = {".": dp("256"), ",": dp("2"), "?": dp("236"), "!": dp("235")}
BLANK = chr(0x2800)


def to_braille(text: str) -> str:
    out = []
    num_mode = False
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            idx = code - 0xAC00
            cho = CHO_LIST[idx // 588]
            jung = JUNG_LIST[(idx % 588) // 28]
            jong = JONG_LIST[idx % 28]
            out.append(CHO_BR.get(cho, "") + JUNG_BR.get(jung, "") + JONG_BR.get(jong, ""))
            num_mode = False
        elif ch in DIGIT_BR:
            if not num_mode:
                out.append(NUM_SIGN)
                num_mode = True
            out.append(DIGIT_BR[ch])
        elif ch.lower() in LATIN_BR:
            out.append(LATIN_BR[ch.lower()])
            num_mode = False
        elif ch in PUNCT_BR:
            out.append(PUNCT_BR[ch])
            num_mode = False
        elif ch == "\n":
            out.append("\n")
            num_mode = False
        elif ch.isspace():
            out.append(BLANK)
            num_mode = False
        else:
            out.append(ch)
            num_mode = False
    return "".join(out)


# ------------------------------------------------------------------
# 브라우저 음성 컴포넌트 (TTS / STT / 경고)
# ------------------------------------------------------------------
def js_text(value: str) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def tts_widget(text: str, label: str = "🔊 소리내어 읽기", rate: float = 1.0, height: int = 130):
    try:
        page = f"""
<div style="font-family:sans-serif;">
  <button id="play" style="font-size:22px;font-weight:700;padding:14px 22px;margin:4px;
    border-radius:14px;border:3px solid {FG};background:{ACCENT};color:{BTN_FG};cursor:pointer;">{label}</button>
  <button id="stop" style="font-size:22px;font-weight:700;padding:14px 22px;margin:4px;
    border-radius:14px;border:3px solid {FG};background:{CARD};color:{FG};cursor:pointer;">⏹ 멈춤</button>
  <div id="msg" style="color:{FG};font-size:16px;margin-top:6px;"></div>
</div>
<script>
const TEXT = {js_text(text)};
const RATE = {float(rate)};
const msg = document.getElementById('msg');
document.getElementById('play').onclick = function() {{
  try {{
    if (!('speechSynthesis' in window)) {{ msg.textContent = '이 브라우저는 음성 읽기를 지원하지 않아요. 크롬 사용을 권장합니다.'; return; }}
    if (!TEXT.trim()) {{ msg.textContent = '읽을 내용이 없어요.'; return; }}
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(TEXT);
    u.lang = 'ko-KR'; u.rate = RATE;
    u.onerror = function() {{ msg.textContent = '음성 재생 중 문제가 생겼어요.'; }};
    window.speechSynthesis.speak(u);
    msg.textContent = '읽는 중...';
    u.onend = function() {{ msg.textContent = '읽기가 끝났어요.'; }};
  }} catch (e) {{ msg.textContent = '음성 기능을 사용할 수 없어요.'; }}
}};
document.getElementById('stop').onclick = function() {{
  try {{ window.speechSynthesis.cancel(); msg.textContent = '멈췄어요.'; }} catch (e) {{}}
}};
</script>
"""
        st_html(page, height=height)
    except Exception:
        st.warning("음성 읽기 기능을 불러오지 못했어요. 페이지를 새로고침해 주세요.")


def stt_widget(font_size: int = 40, height: int = 520):
    try:
        page = f"""
<div style="font-family:sans-serif;color:{FG};">
  <button id="start" style="font-size:22px;font-weight:700;padding:14px 22px;margin:4px;
    border-radius:14px;border:3px solid {FG};background:{ACCENT};color:{BTN_FG};cursor:pointer;">🎤 듣기 시작</button>
  <button id="stop" style="font-size:22px;font-weight:700;padding:14px 22px;margin:4px;
    border-radius:14px;border:3px solid {FG};background:{CARD};color:{FG};cursor:pointer;">⏹ 멈춤</button>
  <button id="clear" style="font-size:22px;font-weight:700;padding:14px 22px;margin:4px;
    border-radius:14px;border:3px solid {FG};background:{CARD};color:{FG};cursor:pointer;">🗑 지우기</button>
  <button id="copy" style="font-size:22px;font-weight:700;padding:14px 22px;margin:4px;
    border-radius:14px;border:3px solid {FG};background:{CARD};color:{FG};cursor:pointer;">📋 복사</button>
  <div id="status" style="font-size:18px;margin:8px 4px;">상태: 대기 중</div>
  <div id="box" style="min-height:300px;max-height:360px;overflow-y:auto;padding:18px;border:3px solid {FG};
    border-radius:18px;background:{CARD};font-size:{font_size}px;font-weight:700;line-height:1.5;word-break:keep-all;"></div>
</div>
<script>
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
const box = document.getElementById('box');
const statusEl = document.getElementById('status');
let rec = null, running = false, finalText = '';
function render(interim) {{
  box.innerHTML = '';
  const f = document.createElement('span'); f.textContent = finalText; box.appendChild(f);
  const i = document.createElement('span'); i.style.opacity = '0.6'; i.textContent = interim || ''; box.appendChild(i);
  box.scrollTop = box.scrollHeight;
}}
if (!SR) {{
  statusEl.textContent = '이 브라우저는 음성 인식을 지원하지 않아요. 크롬(PC/안드로이드) 사용을 권장합니다.';
}} else {{
  rec = new SR();
  rec.lang = 'ko-KR'; rec.continuous = true; rec.interimResults = true;
  rec.onresult = function(e) {{
    let interim = '';
    for (let i = e.resultIndex; i < e.results.length; i++) {{
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) {{ finalText += t + '\\n'; }} else {{ interim += t; }}
    }}
    render(interim);
  }};
  rec.onerror = function(e) {{
    if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {{
      statusEl.textContent = '마이크 권한이 필요해요. 주소창의 마이크 허용을 눌러 주세요.'; running = false;
    }} else if (e.error === 'no-speech') {{
      statusEl.textContent = '소리가 들리지 않아요. 계속 듣고 있어요...';
    }} else {{
      statusEl.textContent = '오류: ' + e.error;
    }}
  }};
  rec.onend = function() {{
    if (running) {{ try {{ rec.start(); }} catch (e) {{}} }}
    else {{ statusEl.textContent = '상태: 멈춤'; }}
  }};
}}
document.getElementById('start').onclick = function() {{
  if (!rec) return;
  try {{ running = true; rec.start(); statusEl.textContent = '상태: 듣는 중... 말씀해 주세요'; }} catch (e) {{ statusEl.textContent = '이미 듣고 있어요.'; }}
}};
document.getElementById('stop').onclick = function() {{
  running = false; try {{ if (rec) rec.stop(); }} catch (e) {{}}
}};
document.getElementById('clear').onclick = function() {{ finalText = ''; render(''); }};
document.getElementById('copy').onclick = function() {{
  try {{
    navigator.clipboard.writeText(finalText).then(function() {{ statusEl.textContent = '복사했어요.'; }},
      function() {{ statusEl.textContent = '복사가 막혀 있어요. 글자를 직접 선택해 복사해 주세요.'; }});
  }} catch (e) {{ statusEl.textContent = '복사가 막혀 있어요. 글자를 직접 선택해 복사해 주세요.'; }}
}};
</script>
"""
        st_html(page, height=height)
    except Exception:
        st.warning("자막 기능을 불러오지 못했어요. 페이지를 새로고침해 주세요.")


def alert_widget(message: str, flash: bool = True, speak: bool = True, height: int = 330):
    try:
        anim = "animation: blink 0.8s infinite;" if flash else ""
        page = f"""
<style>
@keyframes blink {{ 0% {{background:#D90000;color:#FFFFFF;}} 50% {{background:#FFFFFF;color:#D90000;}} 100% {{background:#D90000;color:#FFFFFF;}} }}
#sos {{ font-family:sans-serif;font-size:44px;font-weight:900;text-align:center;padding:40px 10px;
  border:8px solid #000;border-radius:24px;background:#D90000;color:#FFFFFF;{anim} word-break:keep-all; }}
</style>
<button id="go" style="font-size:22px;font-weight:700;padding:12px 20px;margin-bottom:10px;border-radius:14px;
  border:3px solid #000;background:#FFE600;color:#000;cursor:pointer;">🚨 경고 켜기 (소리·진동)</button>
<div id="sos">{message}</div>
<script>
const MSG = {js_text(message)};
const SPEAK = {str(bool(speak)).lower()};
document.getElementById('go').onclick = function() {{
  try {{ if (navigator.vibrate) navigator.vibrate([400, 200, 400, 200, 400]); }} catch (e) {{}}
  try {{
    if (SPEAK && 'speechSynthesis' in window) {{
      window.speechSynthesis.cancel();
      for (let i = 0; i < 3; i++) {{
        const u = new SpeechSynthesisUtterance(MSG); u.lang = 'ko-KR'; u.rate = 0.9;
        window.speechSynthesis.speak(u);
      }}
    }}
  }} catch (e) {{}}
}};
</script>
"""
        st_html(page, height=height)
    except Exception:
        st.warning("경고 화면을 불러오지 못했어요.")


# ------------------------------------------------------------------
# AAC 문구 데이터
# ------------------------------------------------------------------
AAC = {
    "👋 인사": ["👋 안녕하세요", "🙏 감사합니다", "😢 죄송합니다", "✅ 네", "❌ 아니요", "⏳ 잠시만요"],
    "🙋 요청": ["💧 물 주세요", "🚻 화장실에 가고 싶어요", "🆘 도와주세요", "🐢 천천히 말해 주세요",
              "🔁 다시 한 번 말해 주세요", "✍ 글로 써 주세요"],
    "🩺 몸 상태": ["🤕 아파요", "😵 어지러워요", "💊 약이 필요해요", "😴 피곤해요", "🥶 추워요", "🥵 더워요"],
    "🚌 이동": ["🗺 길을 알려 주세요", "🚏 버스 정류장이 어디예요?", "🛗 엘리베이터가 어디예요?",
              "🚕 택시를 불러 주세요", "📍 도착했어요", "🧑‍🦯 안내해 주실 수 있나요?"],
    "🍚 식사": ["🍚 배고파요", "📜 점자 메뉴판이 있나요?", "🌶 맵지 않게 해 주세요",
              "🧾 계산해 주세요", "🍽 포장해 주세요", "🥛 따뜻한 물 주세요"],
}


def strip_emoji(text: str) -> str:
    """앞쪽 이모지를 제거하고 읽을 문장만 남김"""
    parts = text.split(" ", 1)
    return parts[1] if len(parts) == 2 else text


def add_phrase(phrase: str):
    st.session_state.sentence.append(strip_emoji(phrase))


def undo_phrase():
    if st.session_state.sentence:
        st.session_state.sentence.pop()


def clear_sentence():
    st.session_state.sentence = []


def add_free_text():
    value = st.session_state.get("free_in", "").strip()
    if value:
        st.session_state.sentence.append(value)
    st.session_state.free_in = ""


def save_custom_phrase():
    value = st.session_state.get("custom_in", "").strip()
    if value and value not in st.session_state.custom_phrases:
        st.session_state.custom_phrases.append(value)
    st.session_state.custom_in = ""


# ------------------------------------------------------------------
# 메인 화면
# ------------------------------------------------------------------
st.title("♿ 모두의 소리·눈·말")
st.subheader("듣고 · 보고 · 말할 수 있는 접근성 센터")

tab_home, tab_hear, tab_see, tab_speak, tab_sos = st.tabs(
    ["🏠 홈", "👂 듣기(자막)", "👁 보기(음성·점자)", "🗣 말하기(AAC)", "🆘 긴급"]
)

# ---------------- 홈 ----------------
with tab_home:
    st.markdown(
        '<div class="card"><b>사용 방법</b><br>위의 탭에서 필요한 기능을 고르세요. '
        '왼쪽 사이드바에서 글자 크기와 화면 색상을 바꿀 수 있어요. '
        '음성 기능은 <b>크롬 브라우저</b>에서 가장 잘 동작해요.</div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            '<div class="card"><h3>👂 들리지 않을 때</h3>'
            '상대방의 말을 <b>실시간 큰 글씨 자막</b>으로 보여줘요.<br><br>'
            '➡ <b>[듣기(자막)]</b> 탭</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            '<div class="card"><h3>👁 잘 보이지 않을 때</h3>'
            '글을 <b>음성으로 읽어주고</b>, 크게 키우고, <b>점자</b>로 바꿔줘요.<br><br>'
            '➡ <b>[보기(음성·점자)]</b> 탭</div>',
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            '<div class="card"><h3>🗣 말하기 어려울 때</h3>'
            '카드를 눌러 문장을 만들면 <b>대신 말해줘요</b>.<br><br>'
            '➡ <b>[말하기(AAC)]</b> 탭</div>',
            unsafe_allow_html=True,
        )
    c4, c5 = st.columns(2)
    with c4:
        st.markdown(
            '<div class="card"><h3>🖐 손 사용이 어려울 때</h3>'
            '큰 버튼으로 구성했고, 키보드(Tab·Enter)만으로도 조작할 수 있어요. '
            '글자 크기는 최대 36까지 키울 수 있어요.</div>',
            unsafe_allow_html=True,
        )
    with c5:
        st.markdown(
            '<div class="card"><h3>🧠 쉬운 화면이 필요할 때</h3>'
            '그림(이모지) 카드와 짧은 문장으로 구성했어요. '
            '깜빡임 줄이기 옵션으로 편안하게 사용하세요.</div>',
            unsafe_allow_html=True,
        )

# ---------------- 듣기 ----------------
with tab_hear:
    st.header("👂 실시간 자막")
    st.write("**[듣기 시작]** 버튼을 누르고 마이크 사용을 **허용**하면, 들리는 말이 큰 글씨로 나타나요.")
    cap_size = st.slider("자막 글자 크기", 24, 80, 44, key="cap_size")
    stt_widget(font_size=cap_size)
    st.info("조용한 곳에서 상대방이 마이크 가까이에서 말하면 더 정확해요. "
            "음성 인식은 브라우저(크롬)의 기능을 사용해요.")

# ---------------- 보기 ----------------
with tab_see:
    st.header("👁 읽어주기 · 크게 보기 · 점자")
    text_in = st.text_area(
        "여기에 글을 입력하거나 붙여넣으세요",
        value="안녕하세요. 저는 점자와 음성으로 정보를 확인하고 싶어요.",
        height=160,
        key="see_text",
    )
    sub1, sub2, sub3 = st.tabs(["🔊 읽어주기", "🔎 글자 확대", "⠿ 점자 변환"])

    with sub1:
        speed = st.select_slider("읽는 속도", options=[0.6, 0.8, 1.0, 1.2, 1.5], value=1.0)
        tts_widget(text_in, "🔊 소리내어 읽기", rate=float(speed))

    with sub2:
        st.markdown(f'<div class="bigtext">{text_in if text_in.strip() else "글을 입력해 주세요."}</div>',
                    unsafe_allow_html=True)

    with sub3:
        try:
            braille = to_braille(text_in) if text_in.strip() else "글을 입력해 주세요."
            st.markdown(f'<div class="braille">{braille}</div>', unsafe_allow_html=True)
            st.download_button(
                "💾 점자 텍스트 파일 저장",
                data=braille.encode("utf-8"),
                file_name="braille.txt",
                mime="text/plain",
            )
            st.caption("⚠ 약자(줄임 표기)를 생략한 단순 변환이에요. 학습과 참고 용도로 사용해 주세요.")
        except Exception:
            st.error("점자 변환 중 문제가 생겼어요. 다른 글로 다시 시도해 주세요.")
        with st.expander("📖 점자 참고표 보기"):
            st.write("**초성(첫 자음)**")
            st.markdown(" · ".join(f"{k} {v}" for k, v in CHO_BR.items() if v))
            st.write("**모음**")
            st.markdown(" · ".join(f"{k} {v}" for k, v in JUNG_BR.items()))
            st.write("**받침(끝 자음)**")
            st.markdown(" · ".join(f"{k} {v}" for k, v in JONG_BR.items() if k and v))

# ---------------- 말하기 ----------------
with tab_speak:
    st.header("🗣 말하기 보드 (AAC)")
    st.write("카드를 눌러 문장을 만든 뒤 **[말하기]** 버튼을 누르세요.")

    sentence_text = " ".join(st.session_state.sentence)
    st.markdown(
        f'<div class="bigtext">{sentence_text if sentence_text else "카드를 눌러 문장을 만들어 보세요 👇"}</div>',
        unsafe_allow_html=True,
    )
    b1, b2, b3 = st.columns(3)
    b1.button("⬅ 한 칸 지우기", on_click=undo_phrase, use_container_width=True)
    b2.button("🗑 모두 지우기", on_click=clear_sentence, use_container_width=True)
    with b3:
        pass
    tts_widget(sentence_text, "🔊 말하기", rate=0.9, height=120)

    cats = list(AAC.keys())
    if st.session_state.custom_phrases:
        cats.append("⭐ 나의 문구")
    cat_tabs = st.tabs(cats)
    for ci, name in enumerate(cats):
        with cat_tabs[ci]:
            phrases = st.session_state.custom_phrases if name == "⭐ 나의 문구" else AAC[name]
            display = [f"⭐ {p}" for p in phrases] if name == "⭐ 나의 문구" else phrases
            cols = st.columns(3)
            for pi, (shown, raw) in enumerate(zip(display, phrases)):
                with cols[pi % 3]:
                    if name == "⭐ 나의 문구":
                        st.button(shown, key=f"c{ci}_{pi}", on_click=add_free_text_value
                                  if False else None, use_container_width=True) if False else None
                        st.button(shown, key=f"c{ci}_{pi}", on_click=add_phrase,
                                  args=(shown,), use_container_width=True)
                    else:
                        st.button(shown, key=f"c{ci}_{pi}", on_click=add_phrase,
                                  args=(shown,), use_container_width=True)

    st.divider()
    st.subheader("✏ 직접 입력해서 추가")
    st.text_input("하고 싶은 말을 쓰고 [추가]를 누르세요", key="free_in")
    st.button("➕ 문장에 추가", on_click=add_free_text)
    st.text_input("자주 쓰는 문구를 저장해 두세요 (이 화면을 닫기 전까지 유지돼요)", key="custom_in")
    st.button("⭐ 나의 문구로 저장", on_click=save_custom_phrase)

# ---------------- 긴급 ----------------
with tab_sos:
    st.header("🆘 긴급 도움 요청")
    st.write("위급할 때 아래 화면을 상대방에게 보여주세요.")
    sos_msg = st.text_input("보여줄 메시지", value="도와주세요! 119에 연락해 주세요!")
    alert_widget(sos_msg if sos_msg.strip() else "도와주세요!",
                 flash=not reduce_motion, speak=True)

    st.subheader("📇 나의 긴급 정보 카드")
    e1, e2 = st.columns(2)
    with e1:
        name = st.text_input("이름", key="e_name")
        disability = st.text_input("장애 유형·소통 방법 (예: 청각장애, 글로 소통)", key="e_dis")
    with e2:
        contact = st.text_input("보호자 연락처", key="e_contact")
        note = st.text_input("알아야 할 건강 정보 (혈액형, 알레르기 등)", key="e_note")

    def esc(v: str) -> str:
        return (v or "-").replace("<", "&lt;").replace(">", "&gt;")

    st.markdown(
        f'<div class="card"><h3>📇 긴급 정보</h3>'
        f'<b>이름:</b> {esc(name)}<br><b>소통 방법:</b> {esc(disability)}<br>'
        f'<b>보호자 연락처:</b> {esc(contact)}<br><b>건강 정보:</b> {esc(note)}</div>',
        unsafe_allow_html=True,
    )
    st.caption("입력한 정보는 서버에 저장되지 않고 현재 화면에서만 사용돼요.")

    st.markdown(
        '<div class="card"><h3>📞 신고·상담 안내</h3>'
        '🚒 화재·구급: <b>119</b><br>'
        '🚓 범죄·사고: <b>112</b><br>'
        '💬 음성 통화가 어려우면 <b>문자 신고(119, 112)</b>를 이용할 수 있어요.<br>'
        '<small>※ 지역·통신사별 이용 방법은 다를 수 있으니 미리 확인해 두세요.</small></div>',
        unsafe_allow_html=True,
    )

st.divider()
st.caption("© 모두의 소리·눈·말 | 이 앱은 보조 도구이며 의료·법률적 판단을 대신하지 않아요.")
