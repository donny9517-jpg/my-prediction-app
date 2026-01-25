import streamlit as st
import pandas as pd

# 1. 網頁設定 (centered 對手機最友善)
st.set_page_config(page_title="PRO 數據分析", layout="centered")

# 極簡 CSS：確保文字在任何模式下都清晰，避免白畫面
st.markdown("""
    <style>
    h1, h2, h3, p, span, label { color: #1f1f1f !important; }
    .stMetric { background-color: #f8f9fb !important; padding: 10px; border-radius: 10px; border: 1px solid #eaedf2; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數字並更新", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    total_h = len(st.session_state.history)
    st.write(f"🔢 當前總手數: **{total_h}**")
    
    if total_h >= 1:
        # 計算累積命中率 (所有數據)
        win_c = sum(1 for x in st.session_state.history if x in [6, 7, 8])
        cumulative_win_rate = (win_c / total_h) * 100
        st.metric("📈 累積命中率", f"{cumulative_win_rate:.1f}%")
        
        # 偏離度監控 (最近 10 手)
        if total_h >= 10:
            last_10 = st.session_state.history[-10:]
            avg_val = sum(last_10) / 10
            if abs(avg_val - 7) > 1.5:
                st.warning(f"⚠️ 偏離警戒: 重心偏向 {'大' if avg_val > 7 else '小'}號")
            if cumulative_win_rate <= 30:
                st.error("🚨 警告: 累積命中極低!")
    
    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 (原始設定) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    for e in range(2, 13):
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        # 原始連動矩陣
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
    # 36 手週期提醒
    curr_len = len(st.session_state.history)
    if curr_len > 0 and curr_len % 36 == 0:
        st.info(f"💡 **週期提醒**: 已記錄 {curr_len} 手。建議清空數據以保持預測靈敏度。")

    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 置頂推薦
    top_3 = df_res.head(3)
    top_list = top_3['數字'].astype(int).tolist()
    
    st.subheader("🏆 熱門預測 Top 3")
    c1, c2, c3 = st.columns(3)
    c1.metric("首選", top_list[0])
    c2.metric("次選", top_list[1])
    c3.metric("防守", top_list[2])
    
    # 冷門避雷
    bot_2 = df_res.tail(2)['數字'].astype(int).tolist()
    st.write(f"❄️ 冷門避雷: `{bot_2[0]}`, `{bot_2[1]}`")
    
    st.divider()

    # 注碼與盤勢
    best_s = df_res.iloc[0]['評分']
    if best_s > 65: st.error("💰 注碼: 💥 強烈重注")
    elif best_s > 55: st.success("💰 注碼: 🏹 穩健布局")
    else: st.info("💰 注碼: 🛡️ 試探輕注")
    
    trend = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
    st.warning(f"📈 盤勢: {trend}")

    # 圖表 (固定 2-12 順序)
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])
    
    with st.expander("📜 最近 100 手紀錄"):
        st.write(st.session_state.history[-100:][::-1])
else:
    st.info("👋 歡迎使用！請展開左側選單輸入號碼。")
