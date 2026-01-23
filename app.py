import streamlit as st
import pandas as pd

# 1. 基礎設定
st.set_page_config(page_title="PRO 數據終端", layout="wide")

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出數字", 2, 12, 7)
    if st.button("提交數據", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    if len(st.session_state.history) >= 10:
        win_c = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        st.write(f"📈 近 10 手中軸命中率: **{win_c * 10}%**")
    
    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 ---
def analyze(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results).sort_values("評分", ascending=False)

# --- 主畫面 (修正顯示問題) ---
if st.session_state.history:
    df_res = analyze(st.session_state.history)
    best_num = df_
