import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據分析", layout="centered")
st.title("📊 PRO 專業數據終端 (對子強化版)")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 🔍 自動兼容舊數據邏輯 (修復 TypeError) ---
# 如果發現舊數據係單個數字而非元組，自動進行格式轉換
new_history = []
for item in st.session_state.history:
    if isinstance(item, tuple):
        new_history.append(item)
    else:
        new_history.append((item, False)) # 將舊數字轉換為 (數字, 非對子)
st.session_state.history = new_history

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    
    # 對子勾選框
    is_double = st.checkbox("⚠️ 上一手係對子 (e.g., 3-3, 4-4)")
    
    if st.button("提交數字並更新預測", use_container_width=True):
        st.session_state.history.append((val, is_double))
        st.rerun()
    
    st.divider()
    
    total_h = len(st.session_state.history)
    if total_h >= 1:
        # 安全提取數值
        history_vals = [x[0] for x in st.session_state.history]
        win_c = sum(1 for x in history_vals if x in [6, 7, 8])
        st.metric("📈 累積中軸命中率", f"{(win_c/total_h)*100:.1f}%")

    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 (對子權重) ---
def analyze_data(history):
    if not history: return None, 1.0
    last_val, last_is_double = history[-1]
    history_vals = [x[0] for x in history]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    # 風險鎖
    risk_level = 1.0
    if len(history_vals) >= 5:
        if np.std(history_vals[-5:]) > 2.5: risk_level = 0.6
    
    for e in range(2,
