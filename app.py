import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據分析", layout="centered")
st.title("📊 PRO 專業數據終端 (對子強化版)")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 🔍 自動修正舊數據格式 (修復截圖中的 TypeError) ---
clean_history = []
for item in st.session_state.history:
    if isinstance(item, tuple):
        clean_history.append(item)
    else:
        # 將舊的純數字轉換為 (數字, False)
        clean_history.append((item, False))
st.session_state.history = clean_history

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    is_double = st.checkbox("⚠️ 上一手係對子 (e.g., 3-3)")
    
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
        if e == 7: score += 5
        
        # 矩陣連動
        if last_val in [6,7,8] and e in [6,7,8]: score += 18
        if last_val in [4,8,10] and e in [4,8,10]:
