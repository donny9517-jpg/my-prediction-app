import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據分析", layout="centered")
st.title("📊 PRO 專業數據終端 (全能版)")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：進階監控 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數字並更新", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    total_h = len(st.session_state.history)
    if total_h >= 1:
        win_c = sum(1 for x in st.session_state.history if x in [6, 7, 8])
        st.metric("📈 累積中軸命中率", f"{(win_c/total_h)*100:.1f}%")
        
    st.header("💰 資金管理")
    bankroll = st.number_input("本金", value=1000)
    risk_adj = st.slider("激進度 (0.5=建議)", 0.1, 1.0, 0.5)

    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 ---
def analyze_data(history):
    if not history: return None, 1.0
    last = history[-1]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    risk_level = 1.0
    if len(history) >= 5:
        if np.std(history[-5:]) > 2.5: risk_level = 0.6
    
    for e in range(2, 13):
        score = (prob_map[e] / 36) * 100
        if e == 7: score += 5
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        try:
            omit = history[::-1].index(e)
            score += min(omit * 0.5, 10)
        except ValueError:
            score += 10
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22
        
        final_score = score * risk_level
        results.append({"數字": e, "評分": round(final_score, 2)})
    return pd.DataFrame(results), risk_level

# --- 主畫面顯示 ---
if st.session_state.history:
    df_raw, current_risk = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 Top 3 推薦
    top_list = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 深度預測推薦")
    c1, c2, c3 = st.columns(3)
    c1.metric("第一首選", top_list[0])
    c2.metric("第二輔助", top_list[1])
    c3.metric("第三防守", top_list[2])

    # 💰 凱利注碼
    best_score = df_res.iloc[0]['評分']
    p_val = 0.35 + (best_score / 100) * 0.25
    k_f = (1.0 * p_val - (1 - p_val)) / 1.0
    suggested_bet = bankroll * max(0, k_f) * risk_adj
    st.metric("💰 建議注碼", f"${int(suggested_bet)}")

    # 📊 實時能量分布圖
    st.divider()
    st.subheader("📊 實時能量分布評分")
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])

    # 🕵️ 盤勢一致性檢查
    last_5 = st.session_state.history[-5:]
    if len(last_5) >= 3:
        consistency = np.std(last_5)
        if consistency < 1.6:
            st.success("✅ 目前盤勢穩定，預測參考價值高")
        else:
            st.warning("⚠️ 數據跳動劇烈，請減碼觀望")

    # 📜 累積歷史記錄
    st.divider()
    with st.expander("📜 查看累積歷史記錄 (最近 100 手)"):
        # 顯示為橫向列表方便手機閱讀
        st.write(st.session_state.history[-100:][::-1])
else:
    st.info("👋 歡迎！請輸入數據開始分析。")
