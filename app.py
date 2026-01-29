# --- 主畫面顯示 (這部分負責渲染圖表和紀錄) ---
if st.session_state.history:
    df_raw, current_risk = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 顯示前三名推薦
    top_3 = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 深度預測推薦")
    c1, c2, c3 = st.columns(3)
    c1.metric("第一首選", top_3[0])
    c2.metric("第二輔助", top_3[1])
    c3.metric("第三防守", top_3[2])

    # 💰 建議注碼
    best_s = df_res.iloc[0]['評分']
    p_val = 0.35 + (best_s / 100.0) * 0.25
    k_f = (1.0 * p_val - (1.0 - p_val)) / 1.0
    st.metric("💰 建議注碼", f"${int(1000 * max(0, k_f) * 0.5)}")

    # 📊 這裡就是你找的圖表
    st.divider()
    st.subheader("📊 能量分佈評分")
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])

    # 📜 這裡就是累積歷史紀錄
    with st.expander("📜 查看完整歷史紀錄"):
        display_list = [f"{x[0]} {'(對子)' if x[1] else ''}" for x in st.session_state.history]
        st.write(display_list[-100:][::-1]) # 倒序顯示最近100筆
else:
    st.info("👋 歡迎！請在左側輸入數字。圖表與紀錄會在提交後顯示。")
