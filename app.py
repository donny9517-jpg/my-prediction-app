import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁設定
st.set_page_config(page_title="PRO 數據分析 & 凱利計算器", layout="centered")

st.title("📊 PRO 數據終端 & 凱利注碼器")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數字", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 💰 凱利計算器設定
    st.header("💰 資金管理設定")
    bankroll = st.number_input("當前總本金", min_value=100, value=10000, step=100)
    odds = st.number_input("賠率 (1 賠 X)", min_value=0.1, value=1.0, step=0.1)
    risk_level_input = st.slider("凱利激進度 (1=全凱利, 0.5=半凱利)", 0.1, 1.0, 0.5)

    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 ---
def analyze_data(history):
    if not history: return None, 1.0
    last = history[-1]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    # 盤勢風險鎖
    risk_level = 1.0
    if len(history) >= 5:
        std_recent = np.std(history[-5:])
        if std_recent > 2.5: risk_level = 0.6
    
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
    df_res = df_raw.sort_values("評分",
