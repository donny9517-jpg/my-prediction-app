import streamlit as st
import pandas as pd
import numpy as np
import random

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 專業預測終端", layout="centered")

st.markdown("""
    <style>
    h1, h2, h3, p, span, label { color: #1f1f1f !important; }
    .stMetric { background-color: #f8f9fb !important; padding: 15px; border-radius: 12px; border: 1px solid #eaedf2; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 專業數據分析終端")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數字", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    if st.button("🎲 模擬 36 手數據", use_container_width=True):
        sim_data = [random.randint(1, 6) + random.randint(1, 6) for _ in range(36)]
        st.session_state.history.extend(sim_data)
        st.rerun()

    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 (加入遺漏與區間熱度) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    # 計算最近 5 手熱力分佈
    last_5 = history[-5:]
    
    for e in range(2, 13):
        score = (prob_map[e] / 36) * 100
        
        # 1. 7號底薪
        if e == 7: score += 5 
        
        # 2. 原始矩陣
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        
        # 3. 鄰里熱度補償 (✨新因素)
        # 如果目標數字 e 喺最近 5 手嘅鄰近區域，增加擴散分
        for h in last_5:
            if abs(e - h) <= 1: score += 3
        
        # 4. 遺漏追蹤 (✨新因素)
        # 搵出呢個數字最後一次出現係幾多手之前
        try:
            omit_count = history[::-1].index(e)
            # 遺漏愈耐，回歸能量愈高 (最高加 10 分)
            score += min(omit_count * 0.5, 10)
        except ValueError:
            score += 10 # 從未出現過，給予最大回歸分
        
        # 5. 過熱與鄰居修正
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22
            
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results)

# --- 主畫面顯示 ---
if st.session_state.history:
    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 Top 3 推薦
    top_list = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 深度預測推薦")
    c1, c2, c3 = st.columns(3)
    c1.metric("首選", top_list[0])
    c2.metric("次選", top_list[1])
    c3.metric("防守", top_list[2])
    
    # 📈 數據分析看板
    st.divider()
    
    # 單雙分析 (✨新統計)
    odds = sum(1 for x in st.session_state.history[-10:] if x % 2 != 0)
    evens = 10 - odds
    st.write(f"📊 最近 10 手單雙比：**{odds} 單 | {evens} 雙**")
    if odds >= 7: st.warning("⚠️ 預警：單數過熱，留意雙數反彈")
    elif evens >= 7: st.warning("⚠️ 預警：雙數過熱，留意單數反彈")

    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])

    with st.expander("📜 最近 100 手詳細紀錄"):
        st.write(st.session_state.history[-100:][::-1])
else:
    st.info("👋 歡迎！請輸入數據或點擊側邊欄「模擬數據」開始。")
