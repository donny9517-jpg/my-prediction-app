import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 預測強化終端", layout="centered")

st.title("📊 PRO 數據預測強化終端")

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
    if total_h >= 1:
        win_c = sum(1 for x in st.session_state.history if x in [6, 7, 8])
        st.metric("📈 累積中軸命中", f"{(win_c/total_h)*100:.1f}%")
        
        if total_h >= 5:
            std_dev = np.std(st.session_state.history[-10:])
            st.write(f"波動指數 (STD): **{std_dev:.2f}**")

    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 (加入均值回歸預測) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    # 統計全歷史頻率
    total_h = len(history)
    counts = pd.Series(history).value_counts().reindex(range(2,13), fill_value=0)
    
    for e in range(2, 13):
        # 1. 基礎分
        score = (prob_map[e] / 36) * 100
        # 2. 矩陣連動加分
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        # 3. 鄰居補償
        if abs(last - e) == 1: score += 10
        # 4. 過熱懲罰
        if history[-10:].count(e) >= 3: score -= 22
        
        # ✨ 新增：均值回歸預測模組
        # 如果號碼出現頻率低於理論值，增加「回歸補償分」
        theoretical_freq = (prob_map[e] / 36) * total_h
        actual_freq = counts[e]
        if actual_freq < theoretical_freq:
            score += 6  # 賦予回歸能量
            
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results)

# --- 主畫面顯示 ---
if st.session_state.history:
    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 綜合預測推薦
    top_3 = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 綜合預測推薦")
    c1, c2, c3 = st.columns(3)
    c1.metric("第一首選", top_3[0])
    c2.metric("第二輔助", top_3[1])
    c3.metric("第三防守", top_3[2])
    
    # --- ✨ 新增：長龍/趨勢偵測區 ---
    st.divider()
    st.subheader("🐲 趨勢偵測監控")
    
    last_5 = st.session_state.history[-5:]
    if len(last_5) >= 3:
        # 大(8-12) / 小(2-6) 偵測
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
    st.write("📊 即時能量評分圖 (已整合均值回歸)")
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])

    with st.expander("📜 最近紀錄 (倒序)"):
        st.write(st.session_state.history[-100:][::-1])
else:
    st.info("👋 歡迎！請開始輸入號碼以啟動進階預測模組。")
