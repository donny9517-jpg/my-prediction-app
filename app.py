import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據分析", layout="centered")
st.title("📊 PRO 專業數據終端 (對子強化版)")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 🔍 自動修正數據格式 (防止 TypeError) ---
clean_history = []
for item in st.session_state.history:
    if isinstance(item, tuple):
        clean_history.append(item)
    else:
        # 將舊數據轉換為 (數字, 是否對子)
        clean_history.append((item, False))
st.session_state.history = clean_history

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    is_double = st.checkbox("⚠️ 上一手係對子")
    
    if st.button("提交數字並更新預測", use_container_width=True):
        st.session_state.history.append((val, is_double))
        st.rerun()
    
    st.divider()
    
    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 (對子強化版) ---
def analyze_data(history):
    if not history: return None, 1.0
    last_val, last_is_double = history[-1]
    h_vals = [x[0] for x in history]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    # 風險鎖
    risk_level = 1.0
    if len(h_vals) >= 5:
        if np.std(h_vals[-5:]) > 2.5: risk_level = 0.6
    
    for e in range(2, 13):
        score = (prob_map[e] / 36) * 100
        if e == 7: score += 5.0
        
        # 矩陣連動 (修復截圖中的 IndentationError)
        if last_val in [6,7,8] and e in [6,7,8]:
            score += 18.0
        if last_val in [4,8,10] and e in [4,8,10]:
            score += 14.0
        
        # ✨ 對子偏移加分
        if last_is_double:
            if e in [2, 3, 11, 12]: score += 12.0
            if e == last_val: score += 15.0
        
        # 遺漏與熱度 (修復 Try-Except 語法)
        try:
            omit = h_vals[::-1].index(e)
            score += min(omit * 0.5, 10.0)
        except ValueError:
            score += 10.0
            
        if abs(last_val - e) == 1: score += 10.0
        if h_vals[-10:].count(e) >= 3: score -= 22.0
        
        results.append({"數字": e, "評分": round(score * risk_level, 2)})
    return pd.DataFrame(results), risk_level

# --- 主畫面顯示 ---
if st.session_state.history:
    df_raw, current_risk = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # Top 3 推薦
    top_3 = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 深度預測推薦")
    c1, c2, c3 = st.columns(3)
    c1.metric("第一首選", top_3[0])
    c2.metric("第二輔助", top_3[1])
    c3.metric("第三防守", top_3[2])

    # 凱利注碼 (1000本金)
    best_s = df_res.iloc[0]['評分']
    p_val = 0.35 + (best_s / 100.0) * 0.25
    k_f = (1.0 * p_val - (1.0 - p_val)) / 1
