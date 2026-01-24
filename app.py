import streamlit as st
import pandas as pd

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據終端", layout="centered")

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入與警示 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交並更新預測", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    if len(st.session_state.history) >= 10:
        win_c = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_c * 10
        st.write(f"📈 中軸命中率: **{win_rate}%**")
        if win_rate <= 30:
            st.error(f"⚠️ 預警：命中率低於30%！")
    
    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心運算邏輯 (已優化 9 號權重) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        # A. 物理基礎分
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        
        # B. 矩陣連動加成 (9 號強化版)
        # 矩陣 1: 中軸核心 [6, 7, 8]
        if last in [6,7,8] and e in [6,7,8]: score += 18
        
        # 矩陣 2: 大數/偶數擴展圈 [8, 9, 10, 11] - 讓 9 號跟隨大數加分
        if last in [8,9,10,11] and e in [8,9,10,11]: score += 15
        
        # 矩陣 3: 奇數跳位圈 [5, 7, 9, 11] - 讓 9 號跟隨奇數加分
        if last in [5,7,9,11] and e in [5,7,9,11]: score += 12
        
        # C
