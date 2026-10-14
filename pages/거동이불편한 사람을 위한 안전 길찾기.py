import html
from datetime import datetime
from urllib.parse import quote

import folium
import requests
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="모두길 | 접근성 길찾기",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 모두길: accessibility-focused map prototype.
# OpenStreetMap data is best-effort; accident alerts are community reports
# entered during the current app session, not an official live emergency feed.

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
    .hero {
        padding: 1.25rem 1.4rem; border-radius: 18px;
        background: linear-gradient(120deg, #e8f5ef, #edf5ff);
        border: 1px solid #d5e7df; margin-bottom: 1rem;
    }
    .hero h1 {margin: 0 0 .35rem 0; color: #153d32;}
    .hero p {margin: 0; color: #31564d;}
    .small-note {font-size: .88rem; color: #5f6b66;}
    </style>
    <div class="hero">
      <h1>🧭 모두길</h1>
      <p>조금 더 편하고 안전한 이동을 위한 접근성 지도</p>
    </div>
    """,
    unsafe_allow_html=True,
)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
HEADERS = {"User-Agent": "ModuGilAccessibilityPrototype/1.0 (Streamlit demo)"}


def geocode(place: str):
    """Return (lat, lon, display_name), or None if lookup fails."""
    place = place.strip()
    if not place:
        return None
    try:
        response = requests.get(
            NOMINATIM_URL,
            params={"q": place, "format": "jsonv2", "limit": 1},
            headers=HEADERS,
            timeout=8,
        )
        response.raise_for_status()
        results = response.json()
        if not results:
            return None
        item = results[0]
        return float(item["lat"]), float(item["lon"]), item.get("display_name", place)
    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None


def nearby_accessibility(lat: float, lon: float, radius: int = 1200):
    """Fetch OSM elevator/ramp features; returns a list and a status message."""
    query = f"""
    [out:json][timeout:12];
    (
      node(around:{radius},{lat},{lon})["highway"="elevator"];
      node(around:{radius},{lat},{lon})["elevator"];
      node(around:{radius},{lat},{lon})["ramp"="yes"];
      node(around:{radius},{lat},{lon})["kerb"~"lowered|flush"];
      way(around:{radius},{lat},{lon})["highway"="elevator"];
      way(around:{radius},{lat},{lon})["ramp"="yes"];
    );
    out center tags;
    """
    for endpoint in OVERPASS_URLS:
        try:
            response = requests.post(
                endpoint, data={"data": query}, headers=HEADERS, timeout=15
            )
            response.raise_for_status()
            elements = response.json().get("elements", [])
            features = []
            seen = set()
            for element in elements:
                tags = element.get("tags", {})
                if "lat" in element and "lon" in element:
                    plat, plon = float(element["lat"]), float(element["lon"])
                elif "center" in element:
                    plat, plon = float(element["center"]["lat"]), float(element["center"]["lon"])
                else:
                    continue

                if tags.get("highway") == "elevator" or "elevator" in tags:
                    kind, icon, color = "엘리베이터", "🛗", "blue"
                elif tags.get("ramp") == "yes":
                    kind, icon, color = "경사로", "♿", "green"
                elif tags.get("kerb") in ("lowered", "flush"):
                    kind, icon, color = "낮은 턱/턱 낮춤", "♿", "green"
                else:
                    continue

                key = (round(plat, 6), round(plon, 6), kind)
                if key in seen:
                    continue
                seen.add(key)
                features.append(
                    {
                        "lat": plat,
                        "lon": plon,
                        "kind": kind,
                        "icon": icon,
                        "color": color,
                        "name": tags.get("name", kind),
                        "wheelchair": tags.get("wheelchair", "정보 없음"),
                        "access": tags.get("access", "정보 없음"),
                    }
                )
            return features, None
        except (requests.RequestException, ValueError, TypeError):
            continue
    return [], "지도 시설 정보를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요."


def make_map(center, features, reports):
    m = folium.Map(
        location=center,
        zoom_start=15,
        tiles="OpenStreetMap",
        control_scale=True,
    )
    folium.Marker(
        center,
        tooltip="검색한 중심 위치",
        popup="검색한 중심 위치",
        icon=folium.Icon(color="darkpurple", icon="info-sign"),
    ).add_to(m)

    for feature in features:
        popup = (
            f"<b>{html.escape(feature['name'])}</b><br>"
            f"종류: {html.escape(feature['kind'])}<br>"
            f"휠체어 정보: {html.escape(feature['wheelchair'])}<br>"
            f"출입 정보: {html.escape(feature['access'])}<br>"
            "<small>OpenStreetMap 등록 정보이며 현장 상태와 다를 수 있습니다.</small>"
        )
        folium.Marker(
            [feature["lat"], feature["lon"]],
            tooltip=f"{feature['icon']} {feature['kind']}",
            popup=folium.Popup(popup, max_width=280),
            icon=folium.Icon(color=feature["color"], icon="info-sign"),
        ).add_to(m)

    for report in reports:
        popup = (
            f"<b>⚠️ {html.escape(report['type'])}</b><br>"
            f"{html.escape(report['description'])}<br>"
            f"<small>사용자 제보 · {html.escape(report['time'])}</small>"
        )
        folium.Marker(
            [report["lat"], report["lon"]],
            tooltip=f"⚠️ 제보: {report['type']}",
            popup=folium.Popup(popup, max_width=280),
            icon=folium.Icon(color="red", icon="warning-sign"),
        ).add_to(m)
    return m


if "reports" not in st.session_state:
    st.session_state.reports = []
if "origin_result" not in st.session_state:
    st.session_state.origin_result = None
if "destination_result" not in st.session_state:
    st.session_state.destination_result = None
if "search_result" not in st.session_state:
    st.session_state.search_result = None
if "access_features" not in st.session_state:
    st.session_state.access_features = []
if "map_error" not in st.session_state:
    st.session_state.map_error = None

with st.sidebar:
    st.header("🧑‍🦽 이동 설정")
    avoid_stairs = st.checkbox("계단이 있는 길 피하기", value=True)
    prefer_ramps = st.checkbox("경사로가 있는 길 우선", value=True)
    need_elevator = st.checkbox("엘리베이터 필요", value=False)
    st.caption("이 설정은 이동 조건을 기록합니다. 현재 버전은 경로를 직접 계산하지 않으며, 외부 길찾기 결과가 조건을 완전히 반영한다고 보장하지 않습니다.")
    st.divider()
    st.markdown("**지도 범위**")
    radius = st.select_slider(
        "주변 시설 검색 거리",
        options=[500, 800, 1200, 1800, 2500],
        value=1200,
        format_func=lambda x: f"{x}m",
    )
    st.caption("시설 데이터: OpenStreetMap 기여자")

tab_map, tab_route, tab_alerts, tab_info = st.tabs(
    ["🗺️ 접근성 지도", "📍 길찾기", "⚠️ 위험 제보", "ℹ️ 이용 안내"]
)

with tab_map:
    st.subheader("주변 경사로와 엘리베이터")
    st.write("주소나 장소를 검색하면 해당 위치 주변의 공개 지도 시설 정보를 찾아봅니다.")
    with st.form("location_search"):
        place_query = st.text_input(
            "장소 또는 주소",
            placeholder="예: 서울역, 서울특별시 중구 세종대로 110",
        )
        submitted = st.form_submit_button("위치 검색 및 시설 불러오기", type="primary")
    if submitted:
        if not place_query.strip():
            st.warning("먼저 장소나 주소를 입력해 주세요.")
        else:
            with st.spinner("위치와 주변 시설을 검색하고 있습니다..."):
                result = geocode(place_query)
                if result is None:
                    st.error("위치를 찾지 못했거나 지도 서비스에 연결할 수 없습니다. 주소를 조금 더 구체적으로 입력해 주세요.")
                    st.session_state.search_result = None
                    st.session_state.access_features = []
                else:
                    st.session_state.search_result = result
                    features, error = nearby_accessibility(result[0], result[1], radius)
                    st.session_state.access_features = features
                    st.session_state.map_error = error

    result = st.session_state.search_result
    if result:
        lat, lon, display_name = result
        st.caption(f"검색 위치: {display_name}")
        features = st.session_state.access_features
        count1, count2, count3 = st.columns(3)
        count1.metric("경사로·낮은 턱", sum(f["kind"] in ("경사로", "낮은 턱/턱 낮춤") for f in features))
        count2.metric("엘리베이터", sum(f["kind"] == "엘리베이터" for f in features))
        count3.metric("현재 세션 제보", len(st.session_state.reports))
        if st.session_state.map_error:
            st.warning(st.session_state.map_error)
        elif not features:
            st.info("이 범위에서 등록된 경사로·엘리베이터 정보를 찾지 못했습니다. 시설이 없다는 뜻은 아니며, 지도 데이터가 누락됐을 수 있습니다.")
        st_folium(
            make_map((lat, lon), features, st.session_state.reports),
            use_container_width=True,
            height=520,
            returned_objects=[],
            key="accessibility_map",
        )
        with st.expander("지도에 표시된 시설 목록"):
            if features:
                for feature in features:
                    st.markdown(
                        f"- **{feature['icon']} {feature['name']}** — {feature['kind']} · "
                        f"휠체어: {feature['wheelchair']} · 출입: {feature['access']}"
                    )
            else:
                st.write("표시할 시설 정보가 없습니다.")
    else:
        st.info("위치 검색을 시작해 보세요. 예시로 '서울역' 또는 원하는 건물의 주소를 입력할 수 있습니다.")
        st_folium(
            folium.Map(location=[37.5665, 126.9780], zoom_start=12, tiles="OpenStreetMap"),
            use_container_width=True,
            height=420,
            returned_objects=[],
            key="starter_map",
        )

with tab_route:
    st.subheader("목적지까지 길찾기")
    st.write("출발지와 목적지를 입력하면 좌표를 확인하고 외부 지도 길찾기를 열 수 있습니다.")
    with st.form("route_form"):
        origin_text = st.text_input("출발지", placeholder="예: 서울역")
        destination_text = st.text_input("목적지", placeholder="예: 서울시청")
        route_submit = st.form_submit_button("위치 확인", type="primary")
    if route_submit:
        if not origin_text.strip() or not destination_text.strip():
            st.warning("출발지와 목적지를 모두 입력해 주세요.")
        else:
            with st.spinner("출발지와 목적지를 확인하고 있습니다..."):
                o = geocode(origin_text)
                d = geocode(destination_text)
            if o is None or d is None:
                st.error("출발지 또는 목적지를 찾지 못했습니다. 주소를 확인하거나 잠시 후 다시 시도해 주세요.")
                st.session_state.origin_result = None
                st.session_state.destination_result = None
            else:
                st.session_state.origin_result = o
                st.session_state.destination_result = d

    o = st.session_state.origin_result
    d = st.session_state.destination_result
    if o and d:
        st.success("두 위치를 확인했습니다.")
        st.markdown(f"**출발지:** {o[2]}")
        st.markdown(f"**목적지:** {d[2]}")
        st.caption(
            "아래 버튼은 외부 지도 서비스로 이동합니다. 경사로·엘리베이터·계단 회피 조건은 외부 서비스에서 별도로 확인해 주세요."
        )
        google_url = (
            "https://www.google.com/maps/dir/?api=1"
            f"&origin={quote(origin_text)}&destination={quote(destination_text)}"
            "&travelmode=walking"
        )
        osm_url = (
            "https://www.openstreetmap.org/directions?"
            f"engine=fossgis_osrm_foot&route={o[0]}%2C{o[1]}%3B{d[0]}%2C{d[1]}"
        )
        col_a, col_b = st.columns(2)
        with col_a:
            st.link_button("Google 지도에서 길찾기 열기", google_url, use_container_width=True)
        with col_b:
            st.link_button("OpenStreetMap 경로 열기", osm_url, use_container_width=True)
        st.info("외부 경로 서비스는 접근성 정보를 충분히 반영하지 않을 수 있습니다. 이동 전 엘리베이터 운영 여부와 공사·사고 정보를 확인하세요.")
    else:
        st.info("출발지와 목적지를 입력하고 위치 확인을 눌러 주세요.")

with tab_alerts:
    st.subheader("주변 위험 정보와 제보")
    st.warning("이 화면은 공식 실시간 사고 알림 서비스가 아닙니다. 제보는 현재 앱 세션에만 저장되며, 앱을 재시작하거나 세션이 끝나면 사라질 수 있습니다.")
    current = st.session_state.search_result
    with st.form("report_form"):
        report_type = st.selectbox(
            "위험 유형",
            ["보도 공사", "엘리베이터 고장", "경사로 통행 방해", "보도 파손", "사고·통행 통제", "기타 위험"],
        )
        report_description = st.text_area(
            "상세 내용",
            placeholder="예: 역 출구 앞 보도 공사로 통행 폭이 좁아졌어요.",
            max_chars=300,
        )
        use_current = st.checkbox(
            "접근성 지도에서 검색한 위치에 제보 등록",
            value=bool(current),
            disabled=not bool(current),
        )
        report_address = st.text_input(
            "제보 위치(장소 또는 주소)",
            placeholder="예: 서울역 1번 출구 앞",
            disabled=bool(use_current and current),
        )
        report_submit = st.form_submit_button("제보 등록")
    if report_submit:
        if not report_description.strip():
            st.warning("상세 내용을 입력해 주세요.")
        elif use_current and current:
            rlat, rlon, rname = current
            st.session_state.reports.insert(
                0,
                {
                    "type": report_type,
                    "description": report_description.strip(),
                    "lat": rlat,
                    "lon": rlon,
                    "place": rname,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                },
            )
            st.success("현재 검색 위치에 제보를 표시했습니다.")
        elif report_address.strip():
            with st.spinner("제보 위치를 확인하고 있습니다..."):
                location = geocode(report_address)
            if location is None:
                st.error("제보 위치를 찾지 못했습니다. 주소를 확인해 주세요.")
            else:
                st.session_state.reports.insert(
                    0,
                    {
                        "type": report_type,
                        "description": report_description.strip(),
                        "lat": location[0],
                        "lon": location[1],
                        "place": location[2],
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    },
                )
                st.success("제보를 현재 세션에 등록했습니다.")
        else:
            st.warning("검색한 위치를 선택하거나 제보 위치를 입력해 주세요.")

    if st.session_state.reports:
        st.markdown("#### 등록된 제보")
        for index, report in enumerate(st.session_state.reports):
            with st.container(border=True):
                st.markdown(f"**⚠️ {report['type']}** · {report['time']}")
                st.write(report["description"])
                st.caption(f"위치: {report['place']}")
                if st.button("이 제보 삭제", key=f"delete_report_{index}"):
                    st.session_state.reports.pop(index)
                    st.rerun()
    else:
        st.info("아직 등록된 제보가 없습니다.")

with tab_info:
    st.subheader("서비스 이용 안내")
    st.markdown(
        """
        - **시설 데이터:** OpenStreetMap에 등록된 엘리베이터, 경사로, 낮은 턱 정보를 조회합니다.
        - **데이터 한계:** 지도에 표시되지 않는 시설이 있을 수 있고, 표시된 시설도 공사나 고장으로 이용할 수 없을 수 있습니다.
        - **길찾기:** 실제 경로 계산은 외부 지도 서비스에서 진행됩니다. 접근성 조건이 보장되지는 않습니다.
        - **위험 제보:** 이 프로토타입의 제보는 현재 세션에만 저장됩니다. 다른 이용자에게 자동 전송되지 않습니다.
        - **긴급 상황:** 앱 정보만 믿지 말고 현장 안내와 공식 안전 공지를 확인하세요. 긴급 상황에서는 현지 긴급 신고 체계를 이용하세요.
        - **개인정보:** 정확한 현재 위치를 자동으로 수집하지 않습니다. 사용자가 입력한 장소만 검색합니다.
        """
    )
    st.markdown(
        "[OpenStreetMap 저작권 및 이용 안내](https://www.openstreetmap.org/copyright) · "
        "[Streamlit Community Cloud 안내](https://docs.streamlit.io/deploy/streamlit-community-cloud)"
    )

st.divider()
st.markdown(
    '<p class="small-note">모두길은 접근성 지도 제작을 위한 시범 앱입니다. 실제 이동 전 현장 상태를 확인해 주세요.</p>',
    unsafe_allow_html=True,
)
