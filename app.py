import streamlit as st
import pandas as pd
import numpy as np
import random

# 1. 網頁基礎設定 (移除所有自定義 CSS 以防白畫面)
st.set_page_config(page_title="PRO 數據分析", layout="centered")

st.title("📊 PRO 專業數據分析終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：功能管理 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數字", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 一鍵模擬測試 (驗證 36手提醒)
    if st.button("🎲 模擬 36 手數據", use_container_width=True):
        sim = [random.randint(1,6) + random.randint(1,6) for _ in range(36)]
        st.session_state.history.extend(sim)
        st.rerun()

    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心運算邏輯 (整合所有預測因素) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    # 物理機率地圖
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    total_h = len(history)
    
    for e in range(2, 13):
        # 1. 基礎分 + 7號回歸補償
        score = (prob_map[e] / 36) * 100
        if e == 7: score += 5
        
        # 2. 原始連動矩陣
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        
        # 3. 遺漏能量 (均值回歸)
        try:
            omit = history[::-1].index(e)
            score += min(omit * 0.5, 10)
        except ValueError:
            score += 10

        # 4. 最近熱力擴散 (最近5手)
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
    
    # 📊 統計指標區
    st.divider()
    last_10 = st.session_state.history[-10:]
    std_v = np.std(last_10)
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.write(f"波動指數(STD): **{std_v:.2f}**")
        win_c = sum(1 for x in st.session_state.history if x in [6, 7, 8])
        st.write(f"累積中軸命中: **{(win_c/curr_len)*100:.1f}%**")
        
    with col_stat2:
        big = sum(1 for x in st.session_state.history[-20:] if x > 7)
        small = sum(1 for x in st.session_state.history[-20:] if x < 7)
        st.write(f"大號:{big} | 小號:{small}")

    # 預測能量圖
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])
    
    # 歷史紀錄
    with st.expander("📜 最近紀錄"):
        st.write(st.session_state.history[-100:][::-1])
else:
    st.info("👋 歡迎！請點擊側邊欄 [ > ] 輸入數字開始。")
