import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據分析", layout="centered")

st.title("📊 PRO 專業數據終端 (增強版)")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：進階監控 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數字並更新預測", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    total_h = len(st.session_state.history)
    if total_h >= 1:
        # A. 累積命中率 (計算全歷史 6,7,8)
        win_c = sum(1 for x in st.session_state.history if x in [6, 7, 8])
        st.metric("📈 累積中軸命中率", f"{(win_c/total_h)*100:.1f}%")
        
        # B. 波動監控 (標準差 - 反映最近10手穩定度)
        if total_h >= 5:
            std_v = np.std(st.session_state.history[-10:])
            st.write(f"波動指數 (STD): **{std_v:.2f}**")
            if std_v < 1.5: st.info("⚡ 狀態: 極度穩定")
            elif std_v > 2.5: st.warning("⚡ 狀態: 劇烈跳動")

    if st.button("🗑️ 清空所有數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心運算邏輯 (整合 7 號強化與遺漏補償) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    for e in range(2, 13):
        # 基礎物理分
        score = (prob_map[e] / 36) * 100
        
        # 1. ✨ 7 號強化：給予底薪加成
        if e == 7: score += 5
        
        # 2. 原始矩陣與連動
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        
        # 3. 遺漏能量追蹤 (Mean Reversion)
        try:
            omit = history[::-1].index(e)
            score += min(omit * 0.5, 10)
        except ValueError:
            score += 10
            
        # 4. 鄰居補償與過熱懲罰
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22
            
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results)

# --- 主畫面顯示 ---
if st.session_state.history:
    # 36 手週期提醒
    curr_len = len(st.session_state.history)
    if curr_len % 36 == 0:
        st.info(f"💡 **週期提醒**: 已記錄 {curr_len} 手數據。建議檢視命中率是否回歸均值。")

    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    # 🏆 Top 3 推薦
    top_3 = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 深度預測推薦")
    c1, c2, c3 = st.columns(3)
    c1.metric("第一首選", top_3[0])
    c2.metric("第二輔助", top_3[1])
    c3.metric("第三防守", top_3[2])
    
    # ✨ 新增：盤勢一致性檢查 (偵測規律是否混亂)
    st.divider()
    last_5 = st.session_state.history[-5:]
    if len(last_5) >= 3:
        consistency = np.std(last_5)
        if consistency < 1.6:
            st.success("✅ 目前盤勢規律，預測參考價值【極高】")
        else:
            st.warning("⚠️ 數據跳動劇烈，請減碼試探或觀望")

    # 能量分布圖表
    st.write("📊 即時能量評分圖")
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])
    
    with st.expander("📜 最近 100 手詳細紀錄"):
        st.write(st.session_state.history[-100:][::-1])
else:
    st.info("👋 歡迎！請點擊側邊欄 [ > ] 輸入數字開始分析。")
