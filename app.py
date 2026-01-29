import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據分析預測終端", layout="centered")

# CSS 優化：確保手機與電腦顯示清晰
st.markdown("""
    <style>
    h1, h2, h3, p, span, label { color: #1f1f1f !important; }
    .stMetric { background-color: #f8f9fb !important; padding: 15px; border-radius: 12px; border: 1px solid #eaedf2; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：統計監控 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數字並更新", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    total_h = len(st.session_state.history)
    st.write(f"🔢 當前總手數: **{total_h}**")
    
    if total_h >= 1:
        # 累積命中率 (6,7,8)
        win_c = sum(1 for x in st.session_state.history if x in [6, 7, 8])
        win_rate = (win_c/total_h)*100
        st.metric("📈 累積中軸命中", f"{win_rate:.1f}%")
        
        # 波動監控 (最近 10 手)
        if total_h >= 5:
            std_dev = np.std(st.session_state.history[-10:])
            st.write(f"波動指數 (STD): **{std_dev:.2f}**")
            if std_dev < 1.2: st.info("⚡ 狀態: 極度集中")
            elif std_dev > 2.8: st.warning("⚡ 狀態: 劇烈跳動")

    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心運算邏輯 (整合 7 號強化版) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    # 統計全歷史頻率用於均值回歸
    total_h = len(history)
    counts = pd.Series(history).value_counts().reindex(range(2,13), fill_value=0)
    
    for e in range(2, 13):
        # 1. 基礎物理分
        score = (prob_map[e] / 36) * 100
        
        # ✨ 新增：7 號強勢回歸補償 (防止 7 號被懲罰得太勁)
        if e == 7:
            score += 5  # 給予 7 號永久性的 5 分底薪加成
        
        # 2. 矩陣連動加分
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        
        # 3. 鄰居補償
        if abs(last - e) == 1: score += 10
        
        # 4. 過熱懲罰 (最近 10 手開過 3 次以上)
        if history[-10:].count(e) >= 3: 
            score -= 22
        
        # 5. 均值回歸補償 (低於理論值則加分)
        theoretical_freq = (prob_map[e] / 36) * total_h
        actual_freq = counts[e]
        if actual_freq < theoretical_freq:
            score += 6 
            
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results)

# --- 主畫面顯示 ---
if st.session_state.history:
    # 36 手週期提醒
    curr_len = len(st.session_state.history)
    if curr_len > 0 and curr_len % 36 == 0:
        st.info(f"💡 **週期提醒**: 已記錄 {curr_len} 手數據（1 個完整週期）。建議觀察數據是否回歸均值。")

    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 綜合預測推薦
    top_3 = df_res.head(3)
    top_list = top_3['數字'].astype(int).tolist()
    
    st.subheader("🏆 綜合預測推薦 (已加強 7 號權重)")
    c1, c2, c3 = st.columns(3)
    c1.metric("第一首選", top_list[0])
    c2.metric("第二輔助", top_list[1])
    c3.metric("第三防守", top_list[2])
    
    # --- 🔍 趨勢偵測區 ---
    st.divider()
    st.subheader("🐲 趨勢偵測監控")
    
    last_5 = st.session_state.history[-5:]
    if len(last_5) >= 3:
        is_big = [x > 7 for x in last_5]
        is_small = [x < 7 for x in last_5]
        
        if all(is_big[-3:]):
            st.warning(f"🔥 偵測到「大號長龍」中 (已連續 {sum(1 for x in reversed(is_big) if x)} 把)")
        elif all(is_small[-3:]):
            st.info(f"🌊 偵測到「小號長龍」中 (已連續 {sum(1 for x in reversed(is_small) if x)} 把)")
        else:
            st.write("✅ 目前盤勢平衡，未偵測到明顯長龍。")

    # 顯示大/小分佈比例條
    over_7 = sum(1 for x in st.session_state.history[-20:] if x > 7)
    under_7 = sum(1 for x in st.session_state.history[-20:] if x < 7)
    total_ou = over_7 + under_7 + 0.01
    st.progress(over_7 / total_ou, text=f"最近 20 手趨勢：大號 {over_7} 次 vs 小號 {under_7} 次")

    st.divider()
    st.write("📊 即時能量評分圖 (已整合均值回歸與中軸補償)")
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])

    with st.expander("📜 最近紀錄 (倒序顯示最近 100 手)"):
        st.write(st.session_state.history[-100:][::-1])
else:
    st.info("👋 **歡迎使用 PRO 終端**")
    st.write("請展開左側選單輸入數字開始分析。系統已為 7 號配置「強勢回歸」加權。")
