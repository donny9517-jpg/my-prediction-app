import streamlit as st
import pandas as pd

# 1. 網頁基礎設定 (優化手機窄螢幕顯示)
st.set_page_config(page_title="PRO 數據分析", layout="centered")

# 🛠️ 強制修正手機版顯示問題：確保文字在任何模式下都不會隱形
st.markdown("""
    <style>
    /* 強制所有文字顏色，防止深色模式干擾 */
    h1, h2, h3, p, span, div, label { color: #1f1f1f !important; }
    .stMetric { background-color: #f0f2f6 !important; padding: 10px; border-radius: 8px; border: 1px solid #d1d5db; }
    [data-testid="stMetricValue"] { color: #d33682 !important; font-weight: bold !important; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：手機版要撳左上角箭頭先見到 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("輸入最新號碼", 2, 12, 7)
    if st.button("提交數據並更新", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 【30% 預告警示邏輯】
    if len(st.session_state.history) >= 10:
        win_count = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_count * 10
        st.metric("📈 中軸命中率", f"{win_rate}%")
        
        if win_rate <= 30:
            st.error(f"⚠️ 警報：命中率僅 {win_rate}%！盤勢極亂。")
        elif win_rate >= 70:
            st.success("🔥 規律極強，信心增加")
    else:
        st.info("輸入 10 手後顯示命中率")

    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心運算邏輯 ---
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

# --- 主畫面：針對手機排版優化 ---
if st.session_state.history:
    df_res = analyze_data(st.session_state.history)
    best_num = df_res.iloc[0]['數字']
    conf_score = df_res.iloc[0]['評分']
    
    # 看板採用垂直排列，確保手機唔會擠埋一堆
    st.write("---")
    st.metric("🎯 重點布局", f"{int(best_num)}")
    
    # 注碼建議與變盤預警整合
    if conf_score > 65:
        st.error("💰 注碼建議：💥 強烈重注")
    elif conf_score > 55:
        st.success("💰 注碼建議：🏹 穩健布局")
    else:
        st.info("💰 注碼建議：🛡️ 試探輕注")
        
    trend_text = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
    st.warning(f"📈 目前盤勢：{trend_text}")
    st.write("---")

    # 能量分佈圖
    st.bar_chart(df_res.set_index("數字")["評分"])
    
    # 紀錄表 (設定適合手機的高度)
    st.write("### 📜 最近 100 手紀錄")
    hist_data = st.session_state.history[-100:][::-1]
    df_hist = pd.DataFrame({"號碼": hist_data})
    st.dataframe(df_hist, use_container_width=True, height=250)
else:
    # 呢段係你手機截圖見到嘅提示字句，我加強咗顏色
    st.warning("👈 **請點擊左上角 [ > ] 展開選單輸入數據**")
    st.info("數據僅暫存，刷新網頁會清空。")
