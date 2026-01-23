import streamlit as st
import numpy as np

# 介面設定
st.set_page_config(page_title="專業預測數據終端", layout="wide")
st.title("📊 數據分析預測終端 (Web版)")

# 初始化數據（不保存，重新整理即清空）
if 'data' not in st.session_state:
    st.session_state.data = []

# --- 左側：輸入區 ---
with st.sidebar:
    st.header("數據輸入")
    new_val = st.number_input("輸入最新開出數字 (2-12)", min_value=2, max_value=12, step=1)
    if st.button("提交數據"):
        st.session_state.data.append(new_val)

# --- 邏輯運算大腦 ---
def calculate_scores(history):
    if not history: return None
    
    scores = {}
    last_val = history[-1]
    
    for e in range(2, 13):
        # 1. 物理概率 (CHOOSE 邏輯)
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        base_score = (prob_map[e] / 36) * 100
        
        # 2. 連動矩陣 (上一手對比)
        matrix_score = 0
        if last_val in [6,7,8] and e in [6,7,8]: matrix_score = 15
        if last_val in [4,8,10] and e in [4,8,10]: matrix_score = 12
        if last_val in [2,12] and e in [5,11]: matrix_score = 10
        
        # 3. 鄰居補償
        neighbor_score = 10 if abs(last_val - e) == 1 else 0
        
        # 總分匯總
        scores[e] = base_score + matrix_score + neighbor_score
        
    return scores

# --- 中間：看板顯示 ---
if st.session_state.data:
    results = calculate_scores(st.session_state.data)
    best_pick = max(results, key=results.get)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("重點布局", best_pick)
    with col2:
        st.metric("目前盤勢", "中軸連動" if st.session_state.data[-1] in [6,7,8] else "隨機震盪")
    with col3:
        st.success("✅ 系統已更新")
    
    # 能量分佈圖
    st.bar_chart(list(results.values()))
else:
    st.info("請在左側輸入第一個數字開始分析")

# --- 底部：歷史紀錄 ---
st.write("### 歷史紀錄", st.session_state.data[::-1])
