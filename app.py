import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據分析", layout="centered")
st.title("📊 PRO 專業數據終端 (對子強化版)")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 🔍 自動修正數據格式 (修復 TypeError) ---
clean_history = []
for item in st.session_state.history:
    if isinstance(item, tuple):
        clean_history.append(item)
    else:
        # 將舊數據自動補全為新格式
        clean_history.append((item, False))
st.session_state.history = clean_history

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    is_double = st.checkbox("⚠️ 呢手係對子 (e.g., 3-3, 4-4)")
    
    if st.button("提交數字並更新預測", use_container_width=True):
        st.session_state.history.append((val, is_double))
        st.rerun()
    
    st.divider()
    
    total_h = len(st.session_state.history)
    if total_h >= 1:
        h_vals = [x[0] for x in st.session_state.history]
        win_c = sum(1 for x in h_vals if x in [6, 7, 8])
        st.metric("📈 累積中軸命中率", f"{(win_c/total_h)*100:.1f}%")

    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 (加入對子偵測與防錯) ---
def analyze_data(history):
    if not history: return None, 1.0
    last_val, last_is_double = history[-1]
    h_vals = [x[0] for x in history]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    risk_level = 1.0
    if len(h_vals) >= 5:
        if np.std(h_vals[-5:]) > 2.5: risk_level = 0.6
    
    for e in range(2, 13):
        score = (prob_map[e] / 36) * 100
        if e == 7: score += 5.0
        
        # 矩陣連動
        if last_val in [6,7,8] and e in [6,7,8]: score += 18.0
        if last_val in [4,8,10] and e in [4,8,10]: score += 14.0
        
        # ✨ 對子強化邏輯
        if last_is_double:
            if e == last_val: score += 15.0
            if e in [2, 3, 1
