import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據分析", layout="centered")

st.title("📊 PRO 專業數據終端 (風險防禦版)")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數字並更新預測", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    total_h = len(st.session_state.history)
    if total_h >= 1:
        win_c = sum(1 for x in st.session_state.history if x in [6, 7, 8])
        st.metric("📈 累積中軸命中率", f"{(win_c/total_h)*100:.1f}%")
        
        if total_h >= 5:
            std_v = np.std(st.session_state.history[-10:])
            st.write(f"長期波動 (STD): **{std_v:.2f}**")

    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心運算邏輯 (整合風險安全鎖) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    # ✨ 盤勢風險因子 (Risk Factor)
    risk_level = 1.0
    if len(history) >= 5:
        std_recent = np.std(history[-5:])
        # 如果最近 5 手標準差大過 2.5，判定為亂盤
        if std_recent > 2.5: 
            risk_level = 0.6  # 評分自動打 6 折
    
    for e in range(2, 13):
        # 基礎分
        score = (prob_map[e] / 36) * 100
        
        # 1. 7 號強化
        if e == 7: score += 5
        
        # 2. 原始矩陣
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        
        # 3. 遺漏補償
        try:
            omit = history[::-1].index(e)
            score += min(omit * 0.5, 10)
        except ValueError:
            score += 10
            
        # 4. 鄰居與過熱
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22
        
        # 🛡️ 套用風險安全鎖
        final_score = score * risk_level
        results.append({"數字": e, "評分": round(final_score, 2)})
        
    return pd.DataFrame(results), risk_level

# --- 主畫面顯示 ---
if st.session_state.history:
    curr_len = len(st.session_state.history)
    if curr_len % 36 == 0:
        st.info(f"💡 **週期提醒**: 已記錄 {curr_len} 手數據。")

    df_raw, current_risk = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 深度預測推薦
    top_3 = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 深度預測推薦")
    
    # 顯示目前風險狀態
    if current_risk < 1.0:
        st.error(f"🚨 **危險警告：盤勢劇烈跳動！** 預測分數已強制下調 40%。")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("第一首選", top_3[0])
    c2.metric("第二輔助", top_3[1])
    c3.metric("第三防守", top_3[2])
    
    st.divider()
    
    # 能量分布圖
    st.write("📊 能量分布評分 (已套用風險修正)")
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])
    
    with st.expander("📜 歷史紀錄"):
        st.write(st.session_state.history[-100:][::-1])
else:
    st.info("👋 歡迎！請開始輸入數據，系統將自動啟動風險防禦機制。")
