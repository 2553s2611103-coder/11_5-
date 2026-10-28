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
