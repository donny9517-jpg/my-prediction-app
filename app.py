import streamlit as st
import pandas as pd
import numpy as np
import random

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據預測終端", layout="centered")

# 極簡 CSS，確保手機版文字清晰
st.markdown("""
    <style>
    h1, h2, h3, p { color: #1f1f1f !important; }
    .stMetric { background-color: #f8f9fb !important; padding: 10px; border-radius: 10px; }
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
    
    # 測試功能
    if st.button("🎲 模擬 36 手數據", use_container_width=True):
        sim = [random.randint(1,6) + random.randint(1,6) for _ in range(36)]
        st.session_state.history.extend(sim)
        st.rerun()

    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    # 原始機率地圖
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    # 全歷史頻率統計
    counts = pd.Series(history).value_counts().reindex(range(2,13), fill_value=0)
    total_h = len(history)

    for e in range(2, 13):
        score = (prob_map[e] / 36) * 100
        
        # 1. ✨ 7號強勢回歸補償
        if e == 7: score += 5
        
        # 2. 原始矩陣與連動
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        
        # 3. 遺漏能量 (遺漏愈耐加分愈多)
        try:
            omit = history[::-1].index(e)
            score += min(omit * 0.5, 10)
        except ValueError:
            score += 10

        # 4. 鄰里熱力區間 (✨新因素)
        for h in history[-5:]:
            if abs(e - h) <= 1: score += 3

        # 5. 過熱與鄰居修正
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22
            
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results)

# --- 主畫面顯示 ---
if st.session_state.history:
    # 36 手週期提醒
    curr_len = len(st.session_state.history)
    if curr_len % 36 == 0:
        st.info(f"💡 週期提醒：已記錄 {curr_len} 手。")

    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 Top 3 推薦
    top_3 = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 深度預測推薦")
    c1, c2, c3 = st.columns(3)
    c1.metric("首選", top_3[0])
    c2.metric("次選", top_3[1])
    c3.metric("防守", top_3[2])
    
    # 📉 統計指標：標準差與比例
    st.divider()
    last_10 = st.session_state.history[-10:]
    std_v = np.std(last_10)
    st.write(f"📊 波動指數 (STD): **{std_v:.2f}**")
    
    # 趨勢條
    big = sum(1 for x in st.session_state.history[-20:] if x > 7)
    small = sum(1 for x in st.session_state.history[-20:] if x < 7)
    st.progress(big / (big + small + 0.1), text=f"大號 {big} vs 小號 {small} (最近20手)")

    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])
else:
    st.info("👋 歡迎！請點擊側邊欄 [ > ] 輸入數字。")
