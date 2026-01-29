import streamlit as st
import pandas as pd
import numpy as np

# 1. 網頁基礎設定
st.set_page_config(page_title="PRO 數據分析", layout="centered")

st.title("📊 PRO 專業數據終端 (增強版)")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新號碼", 2, 12, 7)
    if st.button("提交數字", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    total_h = len(st.session_state.history)
    if total_h >= 1:
        # 累積中軸命中率 (6,7,8)
        win_c = sum(1 for x in st.session_state.history if x in [6, 7, 8])
        st.metric("📈 累積中軸命中", f"{(win_c/total_h)*100:.1f}%")
        
        # 波動監控
        if total_h >= 5:
            std_v = np.std(st.session_state.history[-10:])
            st.write(f"波動指數(STD): **{std_v:.2f}**")

    if st.button("🗑️ 清空數據", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# --- 核心邏輯 (加入趨勢過濾) ---
def analyze_data(history):
    if not history: return None
    last = history[-1]
    results = []
    prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
    
    for e in range(2, 13):
        score = (prob_map[e] / 36) * 100
        # 7號底薪補償
        if e == 7: score += 5
        # 原始連動
        if last in [6,7,8] and e in [6,7,8]: score += 18
        if last in [4,8,10] and e in [4,8,10]: score += 14
        # 遺漏能量
        try:
            omit = history[::-1].index(e)
            score += min(omit * 0.5, 10)
        except ValueError:
            score += 10
        # 過熱與鄰居
        if abs(last - e) == 1: score += 10
        if history[-10:].count(e) >= 3: score -= 22
            
        results.append({"數字": e, "評分": round(score, 2)})
    return pd.DataFrame(results)

# --- 主畫面顯示 ---
if st.session_state.history:
    df_raw = analyze_data(st.session_state.history)
    df_res = df_raw.sort_values("評分", ascending=False)
    
    top_3 = df_res.head(3)['數字'].astype(int).tolist()
    st.subheader("🏆 深度預測推薦")
    c1, c2, c3 = st.columns(3)
    c1.metric("首選", top_3[0])
    c2.metric("次選", top_3[1])
    c3.metric("防守", top_3[2])
    
    # ✨ 新增：盤勢健康度檢查
    st.divider()
    last_5 = st.session_state.history[-5:]
    if len(last_5) >= 3:
        # 檢查最近幾手號碼嘅一致性
        is_consistent = np.std(last_5) < 1.5
        if is_consistent:
            st.success("✅ 目前規律穩定，系統預測參考價值高")
        else:
            st.warning("⚠️ 數據跳動過大，請謹慎參考預測分數")

    # 能量分佈
    st.bar_chart(df_raw.sort_values("數字").set_index("數字")["評分"])
else:
    st.info("👋 歡迎！請開始輸入數據。")
