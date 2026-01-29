import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據分析", layout="centered")
st.title("📊 PRO 專業數據終端 (對子強化版)")

# 初始化數據 (改為儲存元組: (數值, 是否對子))
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：進階監控 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    
    # ✨ 新增：對子勾選框
    is_double = st.checkbox("⚠️ 呢手係對子 (例如 3-3, 4-4)")
    
    if st.button("提交數字並更新預測", use_container_width=True):
        st.session_state.history.append((val, is_double))
        st.rerun()
    
    st.divider()
    
    total_h = len(st.session_state.history)
    if total_h >= 1:
        # 提取純數值作統計
        h_vals = [x[0] for x in st.session_state.history]
        win_c = sum(1 for x in h_vals if x in [6, 7, 8])
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
    last_val, last_is_double = history[-1]
    h_vals = [x[0] for x in history]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    risk_level = 1.0
    if len(h_vals) >= 5:
        if np.std(h_vals[-5:]) > 2.5: risk_level = 0.6
    
    for e in range(2, 13):
        score = (prob_map[e] / 36) * 100
        if e == 7: score += 5
        
        # 矩陣連動
        if last_val in [6,7,8] and e in [6,7,8]: score += 18
        if last_val in [4,8,10] and e in [4,8,10]: score += 14
        
        # ✨ 對子偵測邏輯：對子後容易「執迷規律」或「物理跳躍」
        if last_is_double:
            if e == last_val: score += 15       # 號碼重開加分
            if e in [2, 3,
