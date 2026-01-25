import streamlit as st
import pandas as pd

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據終端", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button { width: 100%; height: 3.5em; border-radius: 12px; font-weight: bold; }
    .stMetric { background-color: #f8f9fb !important; padding: 15px; border-radius: 15px; border: 1px solid #eaedf2; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：進階監控 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出號碼", 2, 12, 7)
    if st.button("提交數字並更新"):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 顯示當前總進度
    total_h = len(st.session_state.history)
    st.write(f"🔢 當前總手數：**{total_h}**")
    
    if total_h >= 100:
        last_100 = st.session_state.history[-100:]
        win_c = sum(1 for x in last_100 if x in [6, 7, 8])
        st.metric("📈 中軸命中率", f"{win_c * 10}%")
        
        avg_val = sum(last_10) / 10
        if abs(avg_val - 7) > 1.5:
            st.warning(f"⚠️ 偏離警戒：重心偏向 {'大' if avg_val > 7 else '小'}號")
            
        if (win_c * 10) <= 30:
            st.error("🚨 警告：命中率極低！")
    
    if st.button("🗑️ 清空所有數據"):
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

# --- 主畫面顯示 ---
if st.session_state.history:
    # ✨ 新增：36 手週期提醒邏輯
    current_len = len(st.session_state.history)
    if current_len > 0 and current_len % 36 == 0:
        st.info(f"💡 **週期提醒**：已記錄 {current_len} 手數據（第 {current_len//36} 個完整週期）。建議點擊左側「清空數據」重置分析，以保持規律靈敏度。")

    df_res = analyze_data(st.session_state.history)
    
    top_3 = df_res.head(3)
    top_3_list = top_3['數字'].astype(int).tolist()
    
    st.subheader("🏆 熱門預測 Top 3")
    c1, c2, c3 = st.columns(3)
    c1.metric("第一首選", top_3_list[0])
    c2.metric("第二次選", top_3_list[1])
    c3.metric("第三防守", top_3_list[2])

    bot_2 = df_res.tail(2)['數字'].astype(int).tolist()
    st.markdown(f"**❄️ 冷門避雷：** `{bot_2[0]}` , `{bot_2[1]}`")
    
    st.divider()
    
    conf_score = df_res.iloc[0]['評分']
    if conf_score > 65: st.error("💰 注碼建議：💥 強烈重注")
    elif conf_score > 55: st.success("💰 注碼建議：🏹 穩健布局")
    else: st.info("💰 注碼建議：🛡️ 試探輕注")
        
    trend_text = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
    st.warning(f"📈 目前盤勢：{trend_text}")

    st.bar_chart(df_res.set_index("數字")["評分"])
    
    with st.expander("📜 查看最近 100 手紀錄"):
        st.write(st.session_state.history[-100:][::-1])
else:
    st.info("👈 請展開左側選單輸入數據開始預測")
