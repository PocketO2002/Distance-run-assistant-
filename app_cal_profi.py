import streamlit as st

# ==================== 頁面基本設定 ====================
st.set_page_config(
    page_title="跑手助理",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 主標題（所有頁面都會顯示） ====================
st.title("🏃‍♂️ 跑手助理")

# ==================== 側邊欄導航 ====================
st.sidebar.title("🏃‍♂️ 跑手助理")
st.sidebar.markdown("---")
selected_page = st.sidebar.radio(
    " ",
    ["首頁", "用戶檔案與心率區間", "訓練記錄", "配速計算器", "訓練歷史"],
    index=0
)

# ==================== 各功能頁面 ====================
if selected_page == "首頁":
    st.markdown("### 專為你和你的學生設計的跑步訓練助手")
    st.write("""
    歡迎使用「跑手助理」！
    這個應用程式專為跑手及教練而設，主要功能包括：
    * 記錄個人資料，並計算跑步時的 **5 個心率訓練區間**
    * 記錄跑步訓練及力量訓練的詳細內容
    * 配速計算器
    * 查看訓練歷史及進度
    請從左側選單選擇功能開始使用。
    """)
    st.markdown("---")
    st.info("💡 小提示：建議先到「用戶檔案與心率區間」設定你的個人資料和最大心率。")
    st.write("**目前版本**：v0.1（基礎結構版）")

elif selected_page == "用戶檔案與心率區間":
    st.header("👤 用戶檔案與心率區間")

    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}

    if not st.session_state.user_profile:
        st.write("請輸入你的姓名、性別、年齡，以及已知的最大心率和靜息心率（可留空）。")

        with st.form(key="profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("姓名", value="")
                sex = st.selectbox("性別", options=["男", "女"])
                age = st.number_input("年齡（歲）", min_value=10, max_value=100, value=25, step=1)
            with col2:
                max_hr_input = st.number_input("已知最大心率（bpm，可留空）", min_value=0, max_value=220, value=0, step=1, help="留空則自動使用 220 - 年齡")
                rest_hr_input = st.number_input("已知靜息心率（bpm，可留空）", min_value=0, max_value=120, value=0, step=1, help="留空則預設為 60")
            submitted = st.form_submit_button("💾 儲存個人資料")
            if submitted:
                st.session_state.user_profile = {
                    "name": name,
                    "sex": sex,
                    "age": age,
                    "max_hr_input": max_hr_input,
                    "rest_hr_input": rest_hr_input
                }
                st.success("✅ 個人資料已成功儲存！")
                st.rerun()

    if st.session_state.user_profile:
        profile = st.session_state.user_profile
        st.subheader(f"歡迎，{profile.get('name', '跑手')}！")
        st.write(f"**性別**：{profile.get('sex', '未設定')}　　**年齡**：{profile.get('age', '未設定')} 歲")

        # 決定使用哪個最大心率與靜息心率
        age_val = profile.get("age", 25)
        max_hr_input = profile.get("max_hr_input", 0)
        if max_hr_input > 0:
            effective_max_hr = max_hr_input
            max_hr_source = "你輸入的值"
        else:
            effective_max_hr = 220 - age_val
            max_hr_source = "220 - 年齡（自動計算）"

        rest_hr_input = profile.get("rest_hr_input", 0)
        if rest_hr_input > 0:
            effective_rest_hr = rest_hr_input
            rest_hr_source = "你輸入的值"
        else:
            effective_rest_hr = 60
            rest_hr_source = "預設 60（未輸入）"

        st.caption(f"最大心率來源：{max_hr_source} → **{effective_max_hr} bpm**")
        st.caption(f"靜息心率來源：{rest_hr_source} → **{effective_rest_hr} bpm**")

        st.divider()
        st.subheader("❤️ Karvonen 公式心率區間（預設顯示）")

        zones = [
            ("🏃 Zone 1 - 恢復 / 熱身區", 0.50, 0.60),
            ("🏃 Zone 2 - 有氧耐力區（基礎訓練）", 0.60, 0.70),
            ("🏃 Zone 3 - 節奏 / 乳酸閾值區", 0.70, 0.80),
            ("🏃 Zone 4 - 無氧耐力 / 速度區", 0.80, 0.90),
            ("🏃 Zone 5 - 最大努力 / 衝刺區", 0.90, 1.00)
        ]

        for zone_name, low_pct, high_pct in zones:
            low_hr = int((effective_max_hr - effective_rest_hr) * low_pct + effective_rest_hr)
            high_hr = int((effective_max_hr - effective_rest_hr) * high_pct + effective_rest_hr)
            st.write(f"**{zone_name}**：{low_hr} - {high_hr} bpm　（{int(low_pct*100)}% - {int(high_pct*100)}% HRR）")

        st.warning("✅ 使用 Karvonen 公式（較個人化）。")

        # === Jack Daniels 心率區間（只保留 Easy、Threshold、Interval） ===
        show_jd = st.checkbox("📊 顯示 Jack Daniels 心率區間（依影片內容）")
        if show_jd:
            st.subheader("Jack Daniels 心率區間（使用 Karvonen 公式）")
            jd_zones = [
                ("E - Easy / 輕鬆跑（約 60%）", 0.58, 0.65),
                ("T - Threshold / 乳酸閾值（82-88%）", 0.82, 0.88),
                ("I - Interval / 間歇跑（97-100%）", 0.97, 1.00)
            ]
            for z_name, low_pct, high_pct in jd_zones:
                low_hr = int((effective_max_hr - effective_rest_hr) * low_pct + effective_rest_hr)
                high_hr = int((effective_max_hr - effective_rest_hr) * high_pct + effective_rest_hr)
                st.write(f"**{z_name}**：{low_hr} - {high_hr} bpm　（{int(low_pct*100)}% - {int(high_pct*100)}% HRR）")

        if st.button("✏️ 修改個人資料"):
            st.session_state.user_profile = {}
            st.rerun()
    else:
        st.info("👆 請在上方填寫資料，然後按「儲存個人資料」按鈕。")

elif selected_page == "訓練記錄":
    st.header("📝 訓練記錄（跑步）")
    st.caption("💡 選擇訓練類型後，先設定 Sets / Reps / Work distance / Rest 時間，再填詳細數據。")

    if 'running_records' not in st.session_state:
        st.session_state.running_records = []

    # 訓練類型選擇
    training_type = st.selectbox(
        "🏃 訓練類型",
        ["Easy", "Tempo", "Short Threshold", "Long Threshold", "VO2 Max Interval", "Specific Interval"],
        index=0
    )

    # 間歇類型設定區
    num_sets = 1
    reps_per_set = 1
    total_reps = 1
    interval_dist = 400
    rest_rep = 30
    rest_set = 2
    if training_type in ["Short Threshold", "Long Threshold", "VO2 Max Interval", "Specific Interval"]:
        st.markdown("**🔢 Interval 設定（決定表格大小 + 預設值）**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            num_sets = st.number_input("Sets", min_value=1, max_value=10, value=4, step=1)
        with col2:
            reps_per_set = st.number_input("Reps/set", min_value=1, max_value=20, value=5, step=1)
        with col3:
            interval_dist = st.number_input("Work/rep (m)", min_value=50, max_value=2000, value=400, step=50)
        with col4:
            rest_rep = st.number_input("Rest/rep (s)", min_value=0, max_value=300, value=30, step=5)
        rest_set = st.number_input("Rest/set (min)", min_value=0, max_value=10, value=2, step=1)
        total_reps = num_sets * reps_per_set

    with st.form(key="running_record_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            record_date = st.date_input("📅 日期", value="today")
            distance = st.number_input("📏 總距離（公里）", min_value=0.1, max_value=100.0, value=5.0, step=0.1)
            time_str = st.text_input("⏱️ 總時間（格式：mm:ss，例如 30:00）", value="30:00")
        with col2:
            avg_hr = st.number_input("❤️ 平均心率（bpm）", min_value=0, max_value=220, value=150, step=1)
            rpe = st.slider("😓 RPE 主觀疲勞感（1=很輕鬆 ～ 10=極限）", min_value=1, max_value=10, value=5, step=1)

        notes = st.text_area("📝 訓練筆記（可選）", height=60)

        # 間歇類型顯示 reps 詳細表格（無 Rest 欄，無 Notes 欄）
        interval_details = []
        if training_type in ["Short Threshold", "Long Threshold", "VO2 Max Interval", "Specific Interval"]:
            st.markdown("**🔄 Interval Reps Details（每趟數據）**")
            work_default = f"{int(interval_dist)}m"
            default_data = [
                {"Rep": i, "Work (m or mm:ss)": work_default, "Avg HR": 0}
                for i in range(1, total_reps + 1)
            ]
            interval_details = st.data_editor(
                default_data,
                num_rows="dynamic",
                use_container_width=True,
                key="interval_editor"
            )

        submitted = st.form_submit_button("💾 儲存這次跑步記錄", use_container_width=True)

        if submitted:
            total_seconds = 0
            if time_str:
                try:
                    parts = time_str.strip().split(":")
                    if len(parts) == 2:
                        m = int(parts[0])
                        s = int(parts[1])
                        total_seconds = m * 60 + s
                    elif len(parts) == 1:
                        total_seconds = int(parts[0]) * 60
                except:
                    total_seconds = 0

            if distance > 0 and total_seconds > 0:
                pace_sec_per_km = total_seconds / distance
                pace_min = int(pace_sec_per_km // 60)
                pace_sec = int(pace_sec_per_km % 60)
                pace_str = f"{pace_min}:{pace_sec:02d}/km"
                time_display = f"{int(total_seconds//60)}:{int(total_seconds%60):02d}"

                new_record = {
                    "日期": str(record_date),
                    "訓練類型": training_type,
                    "Sets": num_sets if training_type in ["Short Threshold", "Long Threshold", "VO2 Max Interval", "Specific Interval"] else "-",
                    "Reps/set": reps_per_set if training_type in ["Short Threshold", "Long Threshold", "VO2 Max Interval", "Specific Interval"] else "-",
                    "Work/rep (m)": interval_dist if training_type in ["Short Threshold", "Long Threshold", "VO2 Max Interval", "Specific Interval"] else "-",
                    "Rest/rep (s)": rest_rep if training_type in ["Short Threshold", "Long Threshold", "VO2 Max Interval", "Specific Interval"] else "-",
                    "Rest/set (min)": rest_set if training_type in ["Short Threshold", "Long Threshold", "VO2 Max Interval", "Specific Interval"] else "-",
                    "總距離(km)": round(distance, 2),
                    "總時間": time_display,
                    "配速": pace_str,
                    "平均心率": avg_hr if avg_hr > 0 else "-",
                    "RPE": rpe,
                    "筆記": notes.strip() if notes.strip() else "-"
                }

                if interval_details:
                    new_record["Interval Details"] = interval_details

                st.session_state.running_records.append(new_record)
                st.success(f"✅ 已儲存！{training_type}　配速：{pace_str}")
            else:
                st.error("❌ 請輸入有效的距離和 mm:ss 時間！")

    st.divider()
    st.subheader("📊 最近跑步記錄（最新 5 筆）")

    if st.session_state.running_records:
        recent_records = st.session_state.running_records[-5:][::-1]
        st.dataframe(recent_records, use_container_width=True, hide_index=True)

        col_a, col_b, col_c = st.columns(3)
        total_distance = sum(r.get("總距離(km)", 0) for r in st.session_state.running_records)
        total_runs = len(st.session_state.running_records)

        with col_a:
            st.metric("總跑步距離", f"{total_distance:.1f} km")
        with col_b:
            st.metric("記錄筆數", f"{total_runs} 次")
        with col_c:
            st.metric("平均配速", "見記錄表")

        if st.button("🗑️ 清空所有跑步記錄（測試用）", type="secondary"):
            st.session_state.running_records = []
            st.rerun()
    else:
        st.info("👆 請選擇類型、設定 Interval 參數（若適用）、填寫資料並儲存。")

elif selected_page == "配速計算器":
    st.header("🏃 配速計算器")
    st.caption("填寫任意兩個欄位，系統會自動計算第三個（適合訓練和比賽使用）")

    col_dist, col_time, col_pace = st.columns(3)

    with col_dist:
        st.markdown("**距離（公里）**")
        st.markdown("<br>", unsafe_allow_html=True)
        dist = st.number_input(
            "距離",
            min_value=0.0,
            value=0.0,
            step=0.1,
            key="dist_col",
            label_visibility="collapsed"
        )

    with col_time:
        st.markdown("**時間**")
        st.caption("輸入格式：分:秒 或 時:分:秒（例如 16:16 或 1:14:02）")
        time_str = st.text_input(
            "時間",
            value="",
            key="time_text",
            label_visibility="collapsed"
        )
        # 解析時間字串
        total_time_sec = 0
        if time_str:
            parts = time_str.split(":")
            try:
                if len(parts) == 2:
                    m = int(parts[0])
                    s = int(parts[1])
                    total_time_sec = m * 60 + s
                elif len(parts) == 3:
                    h = int(parts[0])
                    m = int(parts[1])
                    s = int(parts[2])
                    total_time_sec = h * 3600 + m * 60 + s
            except:
                total_time_sec = 0

    with col_pace:
        st.markdown("**配速**")
        p1, p2 = st.columns(2)
        with p1:
            pm = st.number_input("分", min_value=0, value=0, step=1, key="p_min", label_visibility="visible")
        with p2:
            ps = st.number_input("秒", min_value=0, max_value=59, value=0, step=1, key="p_sec", label_visibility="visible")
        total_pace_sec = pm * 60 + ps

    # 自動計算邏輯
    st.divider()
    if dist > 0 and total_time_sec > 0 and total_pace_sec == 0:
        pace_sec_per_km = total_time_sec / dist
        pace_min = int(pace_sec_per_km // 60)
        pace_sec = int(pace_sec_per_km % 60)

        # 新增：400m 配速 + 速度
        pace_400_sec_total = pace_sec_per_km * 0.4
        pace_400_min = int(pace_400_sec_total // 60)
        pace_400_sec = int(pace_400_sec_total % 60)
        speed_kmh = round(3600 / pace_sec_per_km, 1)

        st.success(f"✅ **配速：{pace_min}:{pace_sec:02d}/km**")
        st.info(f"**400m 配速：{pace_400_min}:{pace_400_sec:02d}/400m**")
        st.info(f"速度約 **{speed_kmh} km/h**")

    elif dist > 0 and total_pace_sec > 0 and total_time_sec == 0:
        total_sec = dist * total_pace_sec
        hh = int(total_sec // 3600)
        mm = int((total_sec % 3600) // 60)
        ss = int(total_sec % 60)
        st.success(f"✅ 計算結果：**總時間 ≈ {hh} 小時 {mm} 分 {ss} 秒**")

    elif total_time_sec > 0 and total_pace_sec > 0 and dist == 0:
        distance_calc = total_time_sec / total_pace_sec
        st.success(f"✅ 計算結果：**距離 ≈ {distance_calc:.2f} 公里**")

    else:
        st.info("👆 請在上面三個欄位中填寫任意兩個，系統會自動計算剩餘的那一個")

elif selected_page == "訓練歷史":
    st.header("📊 訓練歷史")
    st.write("查看你或學生的過往訓練記錄，並以圖表方式顯示進度。")
    st.warning("⚠️ 此功能尚未實作。我們會在下一階段加入資料表格與圖表。")

# ==================== 頁面底部 ====================
st.markdown("---")
st.caption("跑手助理 v0.1 | 使用 Python + Streamlit 開發 | 專為香港中學體育教育及跑手設計")
st.sidebar.markdown("---")
st.sidebar.caption("v0.1 | 跑手助理")
