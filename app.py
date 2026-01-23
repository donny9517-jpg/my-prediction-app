import streamlit as st
import pandas as pd

# 網頁設定
st.set_page_config(page_title="PRO 數據分析終端", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 PRO 數據分析預測終端")

# 初始化數據
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 側邊欄：輸入 ---
with st.sidebar:
    st.header("⌨️ 數據輸入")
    val = st.number_input("最新開出數字", 2, 12, 7)
    if st.button("提交數字", use_container_width=True):
        st.session_state.history.append(val)

# --- 核心邏輯 (轉化自你的超級 Excel 公式) ---
def analyze(history):
    if not history: return None
    
    last = history[-1]
    results = []
    
    for e in range(2, 13):
        # 1. 物理概率
        prob_map = {7:6, 6:5, 8:5, 5:4, 9:4, 4:3, 10:3, 3:2, 11:2, 2:1, 12:1}
        score = (prob_map[e] / 36) * 100
        
        # 2. 矩陣連動 (6,7,8 或 4,8,10)
        if last in [6,7,8] and e in [6,7,8]: score += 15
        if last in [4,8,10] and e in [4,8,10]: score += 12
        
        # 3. 鄰居補償 (距離1)
        if abs(last - e) == 1: score += 10
        
        # 4. 熱度衰減 (近10手開超過3次減分)
        if history.count(e) >= 3: score -= 15
        
        results.append({"數字": e, "評分": round(score, 2)})
    
    return pd.DataFrame(results).sort_values("評分", ascending=False)

# --- 主畫面顯示 ---
if st.session_state.history:
    df = analyze(st.session_state.history)
    best = df.iloc[0]['數字']
    top_score = df.iloc[0]['評分']
    
    # 看板區
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("重點布局", int(best))
    with c2:
        status = "🔥 重注" if top_score > 60 else "⚖️ 輕注"
        st.metric("注碼建議", status)
    with c3:
        trend = "中軸連動" if st.session_state.history[-1] in [6,7,8] else "震盪盤"
        st.metric("目前盤勢", trend)

    # 能量分佈圖
    st.bar_chart(df.set_index("數字")["評分"])
    
    st.write("### 📜 最近 10 手紀錄", st.session_state.history[-10:][::-1])
else:
    st.info("👈 請喺左邊輸入第一個數字開始分析")

if st.button("🗑️ 清空數據"):
    st.session_state.history = []
    st.rerun()
