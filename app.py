import streamlit as st
import pandas as pd

# 1. 網頁基礎設定 (centered 模式最啱手機)
st.set_page_config(page_title="PRO 數據分析", layout="centered")

# 極簡 CSS：確保文字清晰，唔會導致白畫面
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .stMetric { background-color: #f8f9fb !important; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出號碼", 2, 12, 7)
    if st.button("提交並更新預測", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    if len(st.session_state.history) >= 10:
        win_c = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_c * 10
        st.write(f"📈 中軸命中率: **{win_rate}%**")
        if win_rate <= 30:
            st.error("⚠️ 預警：命中率低於30%！")
    
    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 (保持你最滿意嘅原始設定) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        # 物理機率
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        # 原始連動
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        # 鄰居與過熱修正
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3:
            score -= 22 
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results)

# --- 主畫面顯示 ---
if st.session_state.history:
    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 置頂：Top 3
    top_3 = df_res.head(3)
    top_list = top_3['數字'].astype(int).tolist()
    
    st.subheader("🏆 熱門推薦 (置頂)")
    c1, c2, c3 = st.columns(3)
    c1.metric("首選", top_list[0])
    c2.metric("次選", top_list[1])
    c3.metric("防守", top_list[2])
    
    # ❄️ 冷門避雷
    bot_2 = df_res.tail(2)['數字'].astype(int).tolist()
    st.markdown(f"**❄️ 冷門避雷：** `{bot_2[0]}` , `{bot_2[1]}`")
    
    st.divider()

    # 注碼與盤勢
    best_s = df_res.iloc[0]['評分']
    if best_s > 65: st.error("💰 注碼：💥 強烈重注")
    elif best_s > 55: st.success("💰 注碼：🏹 穩健布局")
    else: st.info("💰 注碼：🛡️ 試探輕注")
    
    trend = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
    st.warning(f"📈 盤勢：{trend}")

    # 能量分布圖
    st.write("📊 **能量分布圖**")
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])
    
    with st.expander("📜 最近 100 手紀錄"):
        st.write(st.session_state.history[-100:][::-1])
else:
    # 呢段解決「乜都無」嘅問題
    st.info("👋 **歡迎使用 PRO 預測終端**")
    st.warning("👈 請點擊左上角 [ > ] 符號展開選單輸入號碼。")
