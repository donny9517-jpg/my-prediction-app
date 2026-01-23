import streamlit as st
import pandas as pd

# 1. 網頁基礎設定 (優化手機顯示)
st.set_page_config(page_title="PRO 數據分析", layout="centered")

# 修正手機版「白畫面」問題：強制文字顏色並移除複雜 CSS
st.markdown("""
    <style>
    /* 確保手機版文字在任何模式下都清晰 */
    h1, h2, h3, p, span { color: #1f1f1f !important; }
    .stMetric { background-color: #f0f2f6 !important; padding: 10px; border-radius: 5px; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入與警示 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出數字", 2, 12, 7)
    if st.button("提交數據並更新", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 【勝率回測與 30% 預告警示】
    if len(st.session_state.history) >= 10:
        win_count = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_count * 10
        st.write(f"📈 中軸命中率: **{win_rate}%**")
        
        if win_rate >= 70:
            st.success("🔥 規律極強")
        elif win_rate <= 30:
            st.error("⚠️ 預警：盤勢混亂 (30%或以下)")
            
        # 單雙預警
        last_5 = st.session_state.history[-5:]
        if all(x % 2 != 0 for x in last_5): st.warning("⚠️ 連續 5 手單號")
        elif all(x % 2 == 0 for x in last_5): st.warning("⚠️ 連續 5 手雙號")
    else:
        st.info("輸入 10 手後顯示命中率")

    st.divider()
    if st.button("清空數據", use_container_width=True):
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
    
    # 針對手機版排版，將 Metric 垂直排列或簡化
    st.write("---")
    st.metric("🎯 重點布局", f"{int(best_num)}")
    
    status = "🔥 重注" if conf_score > 65 else ("🏹 穩健" if conf_score > 55 else "🛡️ 輕注")
    st.metric("💰 注碼建議", status)
    
    trend = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
    st.metric("📈 目前盤勢", trend)
    st.write("---")

    st.bar_chart(df_res.set_index("數字")["評分"])
    
    st.write("### 📜 最近 100 手紀錄")
    hist_data = st.session_state.history[-100:][::-1]
    df_hist = pd.DataFrame({"號碼": hist_data})
    st.dataframe(df_hist, use_container_width=True, height=300)
else:
    st.info("👈 請展開左側選單輸入數據")
