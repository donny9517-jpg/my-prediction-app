import streamlit as st
import pandas as pd

# 1. 網頁設定 (針對手機螢幕優化)
st.set_page_config(page_title="PRO 數據分析", layout="centered")

# 強制修正手機版顏色問題
st.markdown("""
    <style>
    /* 強制所有模式下文字為深灰色，避免隱形 */
    h1, h2, h3, p, span, div { color: #262730 !important; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    /* 讓 Metric 組件在手機上更整齊 */
    [data-testid="stMetric"] {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #d1d5db;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入與【30% 命中警示】 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數據", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 【30% 命中預告警示邏輯】
    if len(st.session_state.history) >= 10:
        win_count = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_count * 10
        st.write(f"📈 中軸命中率: **{win_rate}%**")
        
        # 觸發警示
        if win_rate <= 30:
            st.error(f"⚠️ 警告：目前命中率僅 {win_rate}% (低於30%)，盤勢極亂！")
        elif win_rate >= 70:
            st.success("🔥 規律穩定，信心極高")
    else:
        st.info("輸入 10 手後啟動命中監控")

    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 ---
def analyze_data(history):
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

# --- 主畫面 ---
if st.session_state.history:
    df_res = analyze_data(st.session_state.history)
    best_num = df_res.iloc[0]['數字']
    conf_score = df_res.iloc[0]['評分']
    
    # 手機版採用垂直堆疊排列，避免畫面擠壓
    st.metric("🎯 重點布局", f"{int(best_num)}")
    
    # 三級注碼建議
    if conf_score > 65:
        st.error("💰 注碼建議：💥 強烈重注")
    elif conf_score > 55:
        st.success("💰 注碼建議：🏹 穩健布局")
    else:
        st.info("💰 注碼建議：🛡️ 試探輕注")
        
    trend = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
    st.warning(f"📈 目前盤勢：{trend}")

    st.bar_chart(df_res.set_index("數字")["評分"])
    
    # 紀錄表
    st.write("### 📜 最近 100 手紀錄")
    hist_data = st.session_state.history[-100:][::-1]
    df_hist = pd.DataFrame({"號碼": hist_data})
    st.dataframe(df_hist, use_container_width=True, height=300)
else:
    st.info("👈 請展開左側選單輸入數據")
