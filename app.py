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
    
    # 🏆 恢復 Top 3 推薦顯示
    top_list = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 深度預測推薦")
    c1, c2, c3 = st.columns(3)
    c1.metric("第一首選", top_list[0])
    c2.metric("第二輔助", top_list[1])
    c3.metric("第三防守", top_list[2])

    # 💰 凱利注碼 (基於第一首選)
    best_score = df_res.iloc[0]['評分']
    p_val = 0.35 + (best_score / 100) * 0.25
    k_f = (1.0 * p_val - (1 - p_val)) / 1.0
    suggested_bet = bankroll * max(0, k_f) * risk_adj
    
    st.divider()
    st.metric("💰 建議注碼 (凱利公式)", f"${int(suggested_bet)}")
    if current_risk < 1.0:
        st.error("🚨 警告：盤勢混亂，注碼已自動調低。")

    # 🕵️ 奇偶監控
    st.divider()
    st.subheader("🕵️ 奇偶趨勢監控")
    last_6 = st.session_state.history[-6:]
    odds_c = sum(1 for x in last_6 if x % 2 != 0)
    evens_c = len(last_6) - odds_c
    st.write(f"最近 6 手分佈：**{odds_c} 單 | {evens_c} 雙**")
    
    if len(last_6) >= 4:
        if all(x % 2 != 0 for x in last_6[-4:]): st.warning("🔥 偵測到「單數長龍」")
        elif all(x % 2 == 0 for x in last_6[-4:]): st.info("🌊 偵測到「雙數長龍」")
