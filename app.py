import streamlit as st
import pandas as pd

# 1. 網頁基礎設定 (完全移除自定義 CSS 以確保顯示)
st.set_page_config(page_title="PRO分析終端", layout="centered")

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入與命中警示 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    # 增加輸入框高度感，方便手機點擊
    val = st.number_input("最新號碼", 2, 12, 7, key="input_val")
    if st.button("提交數據並更新", use_container_width=True):
        st.session_state.history.append(val)
    
    st.divider()
    
    # 【30% 命中預告警示】
    if len(st.session_state.history) >= 10:
        win_count = sum(1 for x in st.session_state.history[-10:] if x in [6, 7, 8])
        win_rate = win_count * 10
        st.write(f"📈 中軸命中率: **{win_rate}%**")
        
        # 顯示警示
        if win_rate <= 30:
            st.error(f"⚠️ 預警：命中率低({win_rate}%)，盤勢不穩")
        elif win_rate >= 70:
            st.success("🔥 規律穩定")
    else:
        st.info("輸入10手後顯示命中率")

    if st.button("🗑️ 清空所有數據", use_container_width=True):
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

# --- 主畫面：垂直排版優化 ---
if st.session_state.history:
    df_res = analyze_data(st.session_state.history)
    best_num = df_res.iloc[0]['數字']
    conf_score = df_res.iloc[0]['評分']
    
    # 使用 st.write 代替 Metric，因為 Metric 喺手機版最易出錯
    st.markdown(f"### 🎯 重點布局：**{int(best_num)}**")
    
    # 注碼建議
    if conf_score > 65:
        st.error("💰 注碼建議：💥 強烈重注")
    elif conf_score > 55:
        st.success("💰 注碼建議：🏹 穩健布局")
    else:
        st.info("💰 注碼建議：🛡️ 試探輕注")
        
    # 目前盤勢
    trend_text = "🔗 中軸連動" if st.session_state.history[-1] in [6,7,8] else "🌀 震盪盤"
    st.warning(f"📈 目前盤勢：{trend_text}")

    # 能量圖
    st.bar_chart(df_res.set_index("數字")["評分"])
    
    # 紀錄表
    st.write("### 📜 最近100手紀錄")
    hist_data = st.session_state.history[-100:][::-1]
    st.write(hist_data) # 使用最基礎的寫法確保數據顯示
else:
    # 呢段文字會喺未輸入數據時顯示
    st.warning("👈 請點擊左上角 [ > ] 符號展開選單輸入數字")
    st.info("數據暫存於瀏覽器，刷新頁面會清空。")
