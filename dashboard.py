"""
数据分析简历项目集 · 交互式 BI 看板（Plotly）
- 侧边栏导航 + KPI 卡片 + Plotly 交互图表（悬停/缩放/框选/下钻）
- 每个项目支持上传自己的 CSV 进行复用分析，也支持一键运行内置示例
- 运行：streamlit run dashboard.py  (默认 http://localhost:8501)
"""
import os
import sys
import re
import subprocess
import sqlite3
import tempfile
from io import BytesIO
from sqlalchemy import create_engine, inspect, text
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

BASE = os.path.dirname(__file__)
PY = sys.executable
PALETTE = ["#4F46E5", "#06B6D4", "#F59E0B", "#EF4444", "#10B981", "#8B5CF6", "#EC4899", "#14B8A6"]

st.set_page_config(page_title="数据分析项目集 · BI 看板", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# ---------------- 样式 ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, .stApp { font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif; background:#f6f7f9; color:#1f2937; })))))
header[data-testid="stHeader"] { display:none; }
footer { visibility:hidden; }
.main .block-container { padding-top:1.2rem; padding-bottom:2rem; max-width:1200px; }

/* ---- 顶栏 ---- */
.topbar { display:flex; align-items:center; justify-content:space-between; padding:14px 20px; background:#fff; border:1px solid #eceef1; border-radius:14px; margin-bottom:18px; box-shadow:0 1px 2px rgba(16,24,40,.04); })))))
.topbar .tb-name { font-size:18px; font-weight:700; color:#0f172a; })))))
.topbar .tb-sub { font-size:12px; color:#94a3b8; margin-top:2px; })))))
.topbar .tb-status { font-size:12px; color:#16a34a; background:#ecfdf5; border:1px solid #bbf7d0; padding:4px 10px; border-radius:999px; font-weight:500; })))))

/* ---- 侧边栏 ---- */
section[data-testid="stSidebar"] { background:#ffffff; border-right:1px solid #eceef1; })))))
section[data-testid="stSidebar"] .block-container { padding:1rem .6rem 2rem; }
.brand { padding:6px 14px 14px; border-bottom:1px solid #f1f5f9; margin-bottom:10px; })))))
.brand .b-name { font-size:17px; font-weight:700; color:#0f172a; })))))
.brand .b-sub { font-size:11px; color:#94a3b8; margin-top:2px; letter-spacing:.05em; text-transform:uppercase; })))))
.nav-label { font-size:11px; color:#94a3b8; font-weight:600; text-transform:uppercase; letter-spacing:.06em; padding:4px 14px; })))))
section[data-testid="stSidebar"] button { border-radius:10px !important; text-align:left !important; font-weight:500 !important; font-size:14px !important; padding:.5rem .75rem !important; margin:3px 8px !important; border:1px solid transparent !important; transition:all .12s ease; }
section[data-testid="stSidebar"] button[kind="primary"] { background:#4f46e5 !important; color:#fff !important; box-shadow:0 2px 8px rgba(79,70,229,.25); })))))
section[data-testid="stSidebar"] button[kind="primary"]:hover { background:#4338ca !important; })))))
section[data-testid="stSidebar"] button[kind="secondary"] { background:transparent !important; color:#475569 !important; border-color:transparent !important; })))))
section[data-testid="stSidebar"] button[kind="secondary"]:hover { background:#f1f5f9 !important; color:#0f172a !important; })))))
section[data-testid="stSidebar"] button p { font-size:14px !important; margin:0 !important; }

/* ---- KPI 卡片 ---- */
.kpi { background:#fff; border:1px solid #eceef1; border-radius:14px; padding:16px 18px 16px 22px; box-shadow:0 1px 2px rgba(16,24,40,.04); position:relative; overflow:hidden; min-height:96px; margin-bottom:24px; })))))
.kpi::before { content:""; position:absolute; left:0; top:0; bottom:0; width:4px; background:#4f46e5; })))))
.kpi .k-t { font-size:11px; color:#64748b; font-weight:600; letter-spacing:.03em; text-transform:uppercase; })))))
.kpi .k-v { font-size:26px; font-weight:700; color:#0f172a; margin-top:6px; line-height:1.1; })))))
.kpi .k-s { font-size:12px; color:#94a3b8; margin-top:5px; })))))
.kpi.green::before { background:#10b981; } .kpi.green .k-v { color:#047857; })))))
.kpi.amber::before { background:#f59e0b; } .kpi.amber .k-v { color:#b45309; })))))
.kpi.red::before { background:#ef4444; } .kpi.red .k-v { color:#b91c1c; })))))

/* ---- 区块标题 ---- */
.sec { font-size:15px; font-weight:700; color:#0f172a; margin:26px 0 2px; display:flex; align-items:center; gap:8px; })))))
.sec::before { content:""; width:4px; height:16px; background:#4f46e5; border-radius:2px; display:inline-block; })))))
.sub { font-size:13px; color:#94a3b8; margin-bottom:14px; })))))

/* ---- 图表 / 表格：防止重叠，用最小高度兜底 ---- */
.stPlotlyChart { min-height: 400px !important; }
.stPlotlyChart .js-plotly-plot { min-height: 380px !important; }
.stDataFrame, .stTable { border:1px solid #eceef1; border-radius:14px; overflow:hidden; margin:20px 0 30px 0; box-sizing:border-box; })))))
[data-testid="stExpander"] { background:#fff; border:1px solid #eceef1; border-radius:12px; margin-bottom:18px; })))))
.element-container button[kind="primaryFormSubmit"], .stButton > button { border-radius:10px; }
/* 横向块（KPI 卡片行等）增加底部间距，避免与下一元素紧贴 */
[data-testid="stHorizontalBlock"] { gap: 18px !important; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)


def kpi_cards(cards):
    cols = st.columns(len(cards))
    for col, c in zip(cols, cards):
        t, v, s = c[0], c[1], c[2]
        cls = c[3] if len(c) > 3 else ""
        col.markdown(f'<div class="kpi {cls}"><div class="k-t">{t}</div><div class="k-v">{v}</div><div class="k-s">{s}</div></div>', unsafe_allow_html=True)


def sec(title, sub=""):
    st.markdown(f'<div class="sec">{title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="sub">{sub}</div>', unsafe_allow_html=True)


def _finalize_fig(fig, height=400):
    """固定 Plotly 图高，防止响应式压缩导致重叠。"""
    fig.update_layout(
        autosize=False,
        height=height,
        margin=dict(t=40, b=40, l=40, r=20),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
    )
    return fig


def chart_card(fig, title=None, sub=None):
    """把 Plotly 图包进独立卡片，每个图 400px 固定高度，避免前后元素重叠。"""
    if title:
        sec(title, sub)
    with st.container(border=True):
        st.plotly_chart(_finalize_fig(fig), use_container_width=True, config={"responsive": False})


def app_topbar(title, sub):
    st.markdown(f'<div class="topbar"><div><div class="tb-name">{title}</div>'
                f'<div class="tb-sub">{sub}</div></div>'
                f'<div class="tb-status">● 在线分析</div></div>', unsafe_allow_html=True)


def render_nav():
    st.sidebar.markdown('<div class="brand"><div class="b-name">📊 电商智析台</div>'
                        '<div class="b-sub">电商数据分析工作台</div></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="nav-label">分析项目</div>', unsafe_allow_html=True)
    if "nav" not in st.session_state:
        st.session_state.nav = list(PROJECTS.keys())[0]
    for i, k in enumerate(PROJECTS.keys()):
        active = st.session_state.nav == k
        if st.sidebar.button(k, key=f"nav_{i}", use_container_width=True,
                             type="primary" if active else "secondary"):
            st.session_state.nav = k
    st.sidebar.markdown('<div class="nav-label">工作台</div>', unsafe_allow_html=True)
    active = st.session_state.nav == "STUDIO"
    if st.sidebar.button("🛢️ 数据连接工作台", key="nav_studio", use_container_width=True,
                         type="primary" if active else "secondary"):
        st.session_state.nav = "STUDIO"
    st.sidebar.markdown("---")
    st.sidebar.caption("上传 CSV 或连接数据库即可复用分析")
    return st.session_state.nav


def load_raw(folder):
    db = os.path.join(BASE, folder, "ecommerce.db") if folder in ("ecommerce-sales-dashboard", "ecommerce-sql-bi-pipeline") else os.path.join(BASE, folder, {"rfm-customer-segmentation": "transactions.db", "kmeans-customer-clustering": "transactions.db", "supply-chain-forecasting": "supply_chain.db", "inventory-lstm-forecasting": "retail_sales.db", "kpi-anomaly-detection": "kpi.db", "amazon-competitor-analysis": "competitor.db"}[folder])
    conn = sqlite3.connect(db)
    if folder == "ecommerce-sales-dashboard":
        df = pd.read_sql_query("""SELECT o.order_id,o.customer_id,o.product_id,o.quantity,o.order_date,o.country,
            p.name AS product_name,p.category,p.price, o.quantity*p.price AS revenue
            FROM orders o JOIN products p ON o.product_id=p.product_id""", conn)
    elif folder == "ecommerce-sql-bi-pipeline":
        df = pd.read_sql_query("""SELECT o.order_id,o.customer_id,c.state,o.order_date,o.status,
            p.category,oi.price,oi.freight,(oi.price+oi.freight) AS total
            FROM orders o JOIN order_items oi ON o.order_id=oi.order_id
            JOIN products p ON oi.product_id=p.product_id JOIN customers c ON o.customer_id=c.customer_id""", conn)
    elif folder in ("rfm-customer-segmentation", "kmeans-customer-clustering"):
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
    elif folder == "supply-chain-forecasting":
        df = pd.read_sql_query("SELECT * FROM demand", conn)
    elif folder == "inventory-lstm-forecasting":
        df = pd.read_sql_query("SELECT * FROM sales", conn)
    elif folder == "kpi-anomaly-detection":
        df = pd.read_sql_query("SELECT * FROM kpi", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM listings", conn)
    conn.close()
    return df


def run_demo(folder):
    cwd = os.path.join(BASE, folder)
    subprocess.run([PY, os.path.join(cwd, "generate_data.py")], cwd=cwd, capture_output=True, text=True)


def rfm_from_tx(df):
    df = df.copy()
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["amount"] = df["quantity"] * df["unit_price"]
    snap = df["invoice_date"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("customer_id").agg(
        Recency=("invoice_date", lambda x: (snap - x.max()).days),
        Frequency=("invoice_no", "nunique"),
        Monetary=("amount", "sum")).reset_index()
    rfm["R"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    return rfm


def seg_label(r, f, m):
    if r >= 4 and f >= 4 and m >= 4: return "冠军(Champions)"
    if r >= 3 and f >= 3 and m >= 3: return "忠诚(Loyal)"
    if r <= 2 and f <= 2: return "流失客户(Hibernating)"
    if r <= 2 and f >= 3: return "流失风险(At Risk)"
    if r >= 4: return "新客/高活跃(New)"
    return "潜力客户(Potential)"


# ---------------- 各项目渲染 ----------------

def render_sales(df):
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["revenue"] = df["quantity"] * df["price"]
    if "category" not in df: df["category"] = "未分类"
    cats = sorted(df["category"].dropna().astype(str).unique().tolist())
    sel = st.multiselect("品类筛选", cats, default=cats[:6] if len(cats) > 6 else cats)
    sub = df[df["category"].astype(str).isin(sel)] if sel else df
    total = sub["revenue"].sum(); orders = sub["order_id"].nunique()
    cust = sub["customer_id"].nunique(); aov = total / orders if orders else 0
    kpi_cards([("总营收", f"¥{total:,.0f}", "含筛选"), ("订单数", f"{orders:,}", "含筛选"),
               ("活跃客户", f"{cust:,}", "含筛选"), ("客单价", f"¥{aov:,.1f}", "含筛选")])
    m = sub.groupby(sub["order_date"].dt.to_period("M").astype(str))["revenue"].sum().reset_index()
    fig = px.area(m, x="order_date", y="revenue", title="月度营收趋势", template="plotly_white",
                  color_discrete_sequence=["#4F46E5"], labels={"revenue": "营收", "order_date": "月份"})
    fig.update_traces(hovertemplate="%{x}<br>营收 ¥%{y:,.0f}")
    chart_card(fig)
    c1, c2 = st.columns(2)
    with c1:
        cat = sub.groupby("category")["revenue"].sum().sort_values(ascending=False).reset_index()
        chart_card(px.bar(cat, x="category", y="revenue", title="品类销售结构", template="plotly_white",
                               color="revenue", color_continuous_scale="Viridis"))
    with c2:
        cty = sub.groupby("country")["revenue"].sum().sort_values(ascending=False).head(10).reset_index()
        chart_card(px.bar(cty, x="country", y="revenue", title="国家/地区 Top10", template="plotly_white",
                               color="revenue", color_continuous_scale="Tealgrn"))
    tp_col = "product_name" if "product_name" in sub else "product_id"
    tp = sub.groupby(tp_col)["revenue"].sum().sort_values(ascending=False).head(10).reset_index()
    chart_card(px.bar(tp, x=tp_col, y="revenue", title="Top10 产品", template="plotly_white",
                           color="revenue", color_continuous_scale="Oranges"))


def render_sql_bi(df):
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["rev"] = df["total"] if "total" in df else df["price"] + df.get("freight", 0)
    deliv = df[df.get("status", "delivered") == "delivered"] if "status" in df else df
    total = deliv["rev"].sum(); orders = deliv["order_id"].nunique()
    one_time = (df.groupby("customer_id")["order_id"].nunique() == 1).mean() * 100 if "customer_id" in df else 0
    cancel = (df["status"] == "canceled").mean() * 100 if "status" in df else 0
    kpi_cards([("总营收", f"¥{total:,.0f}", "已交付"), ("订单数", f"{orders:,}", "已交付"),
               ("一次性客户", f"{one_time:.1f}%", "留存结构"), ("取消率", f"{cancel:.1f}%", "订单质量")])
    m = deliv.groupby(deliv["order_date"].dt.to_period("M").astype(str))["rev"].sum().reset_index()
    chart_card(px.line(m, x="order_date", y="rev", title="月度营收趋势", template="plotly_white",
                            markers=True, color_discrete_sequence=["#06B6D4"]))
    c1, c2 = st.columns(2)
    with c1:
        if "category" in deliv:
            cat = deliv.groupby("category")["rev"].sum().sort_values(ascending=False).reset_index()
            chart_card(px.bar(cat, x="category", y="rev", title="品类销售", template="plotly_white",
                                   color="rev", color_continuous_scale="Viridis"))
    with c2:
        if "state" in deliv:
            stt = deliv.groupby("state")["rev"].sum().sort_values(ascending=False).reset_index()
            chart_card(px.bar(stt, x="state", y="rev", title="各州销售", template="plotly_white",
                                   color="rev", color_continuous_scale="Tealgrn"))
    if "customer_id" in df:
        rep = df.groupby("customer_id")["order_id"].nunique()
        dist = rep.value_counts().sort_index().reset_index()
        dist.columns = ["购买次数", "客户数"]
        chart_card(px.bar(dist, x="购买次数", y="客户数", title="客户购买频次分布", template="plotly_white",
                               color="客户数", color_continuous_scale="Purples"))


def render_rfm(df):
    rfm = rfm_from_tx(df)
    rfm["Segment"] = rfm.apply(lambda r: seg_label(r.R, r.F, r.M), axis=1)
    summ = rfm.groupby("Segment").agg(客户数=("customer_id", "count"), 总营收=("Monetary", "sum")).reset_index()
    summ["营收占比%"] = (summ["总营收"] / summ["总营收"].sum() * 100).round(1)
    champ = summ.loc[summ["Segment"].str.contains("冠军"), "营收占比%"]
    kpi_cards([("客户总数", f"{len(rfm):,}", ""), ("客群数", f"{len(summ)}", ""),
               ("冠军客群营收占比", f"{champ.iloc[0] if len(champ) else 0:.1f}%", "高价值"),
               ("潜力+忠诚占比", f"{(summ['Segment'].str.contains('忠诚|潜力')).sum()}/8", "可运营")])
    seg_focus = st.selectbox("聚焦客群（筛选散点）", ["全部"] + summ["Segment"].tolist())
    sc = rfm if seg_focus == "全部" else rfm[rfm["Segment"] == seg_focus]
    col1, col2 = st.columns(2)
    with col1:
        chart_card(px.treemap(summ, path=["Segment"], values="总营收", color="营收占比%",
                                   color_continuous_scale="Blues", title="客群营收结构（可下钻）"))
    with col2:
        fig = px.scatter(sc, x="Recency", y="Monetary", color="Segment", size="Frequency",
                         hover_data=["customer_id", "Recency", "Frequency", "Monetary"],
                         title="客户分布：Recency × Monetary", template="plotly_white")
        chart_card(fig)
    chart_card(px.bar(summ, x="Segment", y="客户数", color="Segment", title="各客群客户数",
                           template="plotly_white"))


def render_kmeans(df):
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    rfm = rfm_from_tx(df)
    X = StandardScaler().fit_transform(rfm[["Recency", "Frequency", "Monetary"]])
    km = KMeans(n_clusters=4, random_state=42, n_init=10).fit(X)
    rfm["Cluster"] = km.labels_
    prof = rfm.groupby("Cluster")[["Recency", "Frequency", "Monetary"]].mean().round(1).reset_index()
    kpi_cards([("样本客户", f"{len(rfm):,}", ""), ("聚类数 k", "4", "肘部法"),
               ("最高频客群", f"簇 {prof.loc[prof['Frequency'].idxmax(),'Cluster']}", "最活跃"),
               ("最高价值客群", f"簇 {prof.loc[prof['Monetary'].idxmax(),'Cluster']}", "高消费")])
    pca = PCA(n_components=2).fit_transform(X)
    rfm["PC1"], rfm["PC2"] = pca[:, 0], pca[:, 1]
    cl = st.selectbox("高亮聚类", ["全部"] + sorted(rfm["Cluster"].unique().tolist()))
    fig = px.scatter(rfm if cl == "全部" else rfm[rfm["Cluster"] == cl], x="PC1", y="PC2", color="Cluster",
                     hover_data=["Recency", "Frequency", "Monetary"], title="客户聚类 (PCA 2D)", template="plotly_white")
    chart_card(fig)
    chart_card(px.bar(prof, x="Cluster", y="Monetary", color="Cluster", title="各聚类平均消费金额",
                           template="plotly_white"))


def render_supply(df):
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_percentage_error
    df = df.copy(); df["date"] = pd.to_datetime(df["date"], errors="coerce")
    rows, fc = [], {}
    for pid, g in df.groupby("product_id"):
        g = g.sort_values("date").reset_index(drop=True)
        g["t"] = np.arange(len(g)); g["doy"] = g["date"].dt.dayofyear
        g["sin"] = np.sin(2 * np.pi * g["doy"] / 365); g["cos"] = np.cos(2 * np.pi * g["doy"] / 365)
        tr, te = g.iloc[:-7], g.iloc[-7:]
        mdl = LinearRegression().fit(tr[["t", "sin", "cos"]], tr["demand"])
        mape = mean_absolute_percentage_error(te["demand"], mdl.predict(te[["t", "sin", "cos"]])) * 100
        last = g.iloc[-1]
        ft = np.arange(len(g), len(g) + 7)
        fd = [(last["date"] + pd.Timedelta(days=i + 1)).dayofyear for i in range(7)]
        Xf = np.column_stack([ft, np.sin(2 * np.pi * np.array(fd) / 365), np.cos(2 * np.pi * np.array(fd) / 365)])
        exp = mdl.predict(Xf).sum() * 1.2
        rows.append({"product_id": pid, "MAPE%": round(mape, 1), "current_inventory": int(last["inventory"]),
                     "expected_7d": round(exp, 0), "reorder": "是" if exp > last["inventory"] else "否"})
        fc[pid] = (g, mdl, exp, last["inventory"])
    res = pd.DataFrame(rows)
    kpi_cards([("产品数", f"{len(res)}", ""), ("平均MAPE", f"{res['MAPE%'].mean():.1f}%", "预测精度"),
               ("需补货", f"{(res['reorder']=='是').sum()}/{len(res)}", "库存预警"),
               ("补货量合计", f"{int(res.loc[res['reorder']=='是','expected_7d'].sum()):,}", "未来7天")])
    pid = st.selectbox("选择产品查看预测曲线", sorted(fc.keys()))
    g, mdl, exp, inv = fc[pid]
    fut_dates = [g["date"].iloc[-1] + pd.Timedelta(days=i + 1) for i in range(7)]
    fd = np.array([d.dayofyear for d in fut_dates])
    Xf = np.column_stack([np.arange(len(g), len(g) + 7), np.sin(2 * np.pi * fd / 365), np.cos(2 * np.pi * fd / 365)])
    future = pd.DataFrame({"date": fut_dates, "demand": mdl.predict(Xf)})
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=g["date"], y=g["demand"], name="历史需求", line=dict(color="#4F46E5")))
    fig.add_trace(go.Scatter(x=future["date"], y=future["demand"], name="未来7天预测", line=dict(color="#F59E0B", dash="dot")))
    fig.update_layout(title=f"产品 {pid} 需求预测（当前库存 {inv}）", template="plotly_white")
    chart_card(fig)
    chart_card(px.bar(res, x="product_id", y="expected_7d", color="reorder", title="各产品未来7天预测需求",
                           template="plotly_white"))
    st.dataframe(res)


def render_lstm(df):
    from sklearn.ensemble import RandomForestRegressor
    df = df.copy(); df["date"] = pd.to_datetime(df["date"], errors="coerce"); df = df.sort_values(["product_id", "date"])
    rows, fc = [], {}
    for pid, g in df.groupby("product_id"):
        s = g["sales"].values.astype(float); W, H = 30, 7
        X = np.array([s[i:i + W] for i in range(len(s) - W - H)]); y = np.array([s[i + W:i + W + H] for i in range(len(s) - W - H)])
        k = int(len(X) * 0.85)
        m = RandomForestRegressor(n_estimators=60, random_state=42, n_jobs=-1).fit(X.reshape(len(X), -1), y)
        fut = m.predict(s[-W:].reshape(1, -1))[0]
        stock = int(g["sales"].iloc[-1] * np.random.randint(3, 8))
        rows.append({"product_id": pid, "未来7天预测": round(fut.sum(), 0), "当前库存": stock, "预警": "⚠️缺货风险" if fut.sum() > stock else "库存充足"})
        fc[pid] = (g, fut, stock)
    res = pd.DataFrame(rows)
    kpi_cards([("产品数", f"{len(res)}", ""), ("缺货风险", f"{(res['预警'].str.contains('风险')).sum()}/{len(res)}", ""),
               ("最高预测", f"{int(res['未来7天预测'].max()):,}", "单品"), ("平均预测", f"{int(res['未来7天预测'].mean()):,}", "单品")])
    pid = st.selectbox("选择产品查看预测", sorted(fc.keys()))
    g, fut, stock = fc[pid]
    fut_days = [g["date"].iloc[-1] + pd.Timedelta(days=i + 1) for i in range(7)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=g["date"], y=g["sales"], name="历史销量", line=dict(color="#06B6D4")))
    fig.add_trace(go.Scatter(x=fut_days, y=fut, name="未来7天预测", line=dict(color="#EF4444", dash="dot")))
    fig.update_layout(title=f"产品 {pid} 销量预测（当前库存 {stock}）", template="plotly_white")
    chart_card(fig)
    chart_card(px.bar(res, x="product_id", y="未来7天预测", color="预警", title="各产品预测与预警",
                           template="plotly_white"))


def render_kpi(df):
    df = df.copy(); df["date"] = pd.to_datetime(df["date"], errors="coerce"); df = df.sort_values("date").reset_index(drop=True)
    thr = st.slider("异常判定阈值 (Z-Score)", 1.5, 5.0, 3.0, 0.1)
    roll = df["revenue"].rolling(30, min_periods=10).mean()
    std = df["revenue"].rolling(30, min_periods=10).std().fillna(df["revenue"].std())
    z = (df["revenue"] - roll) / std
    df["anomaly"] = (z.abs() > thr).astype(int)
    kpi_cards([("监测天数", f"{len(df)}", ""), ("异常天数", f"{int(df['anomaly'].sum())}", f"Z>{thr}"),
               ("平均营收", f"¥{df['revenue'].mean():,.0f}", ""), ("峰值", f"¥{df['revenue'].max():,.0f}", "")])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["revenue"], name="营收", line=dict(color="#4F46E5")))
    an = df[df["anomaly"] == 1]
    fig.add_trace(go.Scatter(x=an["date"], y=an["revenue"], mode="markers", name="异常",
                             marker=dict(color="#EF4444", size=10, symbol="circle-open")))
    fig.update_layout(title="KPI 异常检测（点击图例可隐藏/显示）", template="plotly_white",
                      yaxis_title="营收", xaxis_title="日期")
    chart_card(fig)
    if len(an):
        chart_card(px.bar(an.assign(z=z[df["anomaly"] == 1].values), x="date", y="z", title="异常日 Z-Score",
                               color_discrete_sequence=["#EF4444"], template="plotly_white"))


def render_amazon(df):
    df = df.copy(); df["date"] = pd.to_datetime(df["date"], errors="coerce")
    asins = sorted(df["asin"].astype(str).unique().tolist())
    sel = st.multiselect("竞品筛选", asins, default=asins[:5] if len(asins) > 5 else asins)
    sub = df[df["asin"].astype(str).isin(sel)] if sel else df
    rows = []
    last_date = sub["date"].max()
    lr = sub[sub["date"] == last_date]
    for asin, g in sub.groupby("asin"):
        g = g.sort_values("date"); last = g.iloc[-1]
        share = (1 / last["bsr"]) / sum(1 / lr.groupby("asin")["bsr"].last())
        rows.append({"竞品": str(last.get("name", asin)), "最新BSR": int(last["bsr"]), "最新价格": last["price"],
                     "评论数": int(last["reviews"]), "平均评分": round(g["rating"].mean(), 2), "估计份额%": round(share * 100, 1)})
    res = pd.DataFrame(rows).sort_values("最新BSR")
    kpi_cards([("竞品数", f"{len(res)}", ""), ("市场领先", str(res.iloc[0]["竞品"]), f"BSR {res.iloc[0]['最新BSR']}"),
               ("最高评分", f"{res['平均评分'].max():.2f}", ""), ("平均份额", f"{res['估计份额%'].mean():.1f}%", "")])
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        for asin, g in sub.groupby("asin"):
            fig.add_trace(go.Scatter(x=g["date"], y=g["bsr"], name=str(g.iloc[-1].get("name", asin)), mode="lines"))
        fig.update_layout(title="BSR 排名趋势（越低越好）", template="plotly_white", yaxis=dict(autorange="reversed"))
        chart_card(fig)
    with c2:
        fig2 = go.Figure()
        for asin, g in sub.groupby("asin"):
            fig2.add_trace(go.Scatter(x=g["date"], y=g["price"], name=str(g.iloc[-1].get("name", asin)), mode="lines"))
        fig2.update_layout(title="价格趋势", template="plotly_white")
        chart_card(fig2)
    chart_card(px.scatter(sub, x="price", y="rating", color="asin", size="reviews", hover_data=["name", "bsr"],
                               title="价格 × 评分 × 评论数（气泡大小=评论数）", template="plotly_white"))
    chart_card(px.bar(res, x="竞品", y="估计份额%", color="估计份额%", color_continuous_scale="Viridis",
                           title="估计市场份额", template="plotly_white"))


# ============================================================
#  数据连接工作台（Power BI 风格：连接数据库 / 上传文件 → SQL → 交互分析）
#  开源参考：PyGWalker(拖拽探索)、Apache Superset(SQL Lab)、Evidence(SQL 驱动)、
#           Metabase(GUI 问数)、ydata-profiling(一键 EDA)
# ============================================================

def _build_sqlite_from_frames(frames: dict):
    """把若干 DataFrame 写入一个临时 SQLite 库，返回 (engine, 表名列表, 路径)。"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    eng = create_engine(f"sqlite:///{path}")
    names = []
    for raw, d in frames.items():
        name = re.sub(r"\W+", "_", str(raw))[:63] or "data"
        d.to_sql(name, eng, if_exists="replace", index=False)
        names.append(name)
    return eng, names, path


def _chart_from_spec(df, ch_type, x, y, agg, color, title):
    """根据字段面板配置生成 Plotly 图（借鉴 Power BI 的 轴/图例/值 映射）。"""
    color_col = None if color == "无" else color
    if ch_type == "热力图(相关性)":
        num = df.select_dtypes(include=[np.number])
        corr = num.corr()
        return px.imshow(corr, text_auto=".2f", title=title, template="plotly_white", color_continuous_scale="RdBu_r")
    grouped = agg != "无(明细)" and ch_type in ("柱状图", "折线图", "面积图", "饼图")
    g = df.groupby(x, as_index=False).agg({y: agg}) if grouped else df
    if ch_type == "柱状图":
        return px.bar(g, x=x, y=y, color=color_col, title=title, template="plotly_white")
    if ch_type == "折线图":
        return px.line(g, x=x, y=y, color=color_col, title=title, template="plotly_white", markers=True)
    if ch_type == "面积图":
        return px.area(g, x=x, y=y, color=color_col, title=title, template="plotly_white")
    if ch_type == "散点图":
        return px.scatter(df, x=x, y=y, color=color_col, title=title, template="plotly_white")
    if ch_type == "饼图":
        return px.pie(g, names=x, values=y, title=title, template="plotly_white")
    if ch_type == "箱线图":
        return px.box(df, x=x, y=y, color=color_col, title=title, template="plotly_white")
    if ch_type == "直方图":
        return px.histogram(df, x=x, color=color_col, title=title, template="plotly_white")
    return px.bar(g, x=x, y=y, title=title, template="plotly_white")


def render_studio():
    app_topbar("🛢️ 数据连接工作台", "像 Power BI 一样：连接数据库 / 上传文件 → 写 SQL → 交互式探索")
    with st.expander("💡 本工作台借鉴的开源项目", expanded=False):
        st.markdown("""
        - **PyGWalker**（Kanaries）：把 DataFrame 变成 Tableau/Power BI 式拖拽探索 —— 本页「字段面板」即借鉴其体验
        - **Apache Superset**：SQL Lab + 可视化 —— 本页「SQL 查询」借鉴之
        - **Evidence**：用 SQL 直接驱动数据应用 —— 本页「SQL → 图表」流程借鉴之
        - **Metabase**：GUI 式即席查询 —— 本页「智能聚合」借鉴之
        - **ydata-profiling**：一键 EDA 报告 —— 本页「数据画像」借鉴之
        """)

    src = st.radio("① 选择数据源", ["CSV 上传", "Excel 上传", "SQLite 文件", "数据库连接(URI)", "用内置电商库体验"],
                   horizontal=True)

    if src == "CSV 上传":
        f = st.file_uploader("上传 CSV", type=["csv"], key="st_csv")
        if f and st.button("🔗 连接", key="st_csv_b"):
            df = pd.read_csv(BytesIO(f.getvalue()))
            eng, tables, path = _build_sqlite_from_frames({"data": df})
            st.session_state.studio = {"engine": eng, "tables": tables, "path": path, "source": f.name}
            st.success(f"已连接：{df.shape[0]} 行 × {df.shape[1]} 列")
    elif src == "Excel 上传":
        f = st.file_uploader("上传 Excel", type=["xlsx", "xls"], key="st_xls")
        if f and st.button("🔗 连接", key="st_xls_b"):
            xls = pd.ExcelFile(BytesIO(f.getvalue()))
            frames = {s: xls.parse(s) for s in xls.sheet_names}
            eng, tables, path = _build_sqlite_from_frames(frames)
            st.session_state.studio = {"engine": eng, "tables": tables, "path": path, "source": f.name}
            st.success(f"已连接：{len(tables)} 个 Sheet → {', '.join(tables)}")
    elif src == "SQLite 文件":
        f = st.file_uploader("上传 SQLite 数据库", type=["db", "sqlite", "sqlite3"], key="st_db")
        if f and st.button("🔗 连接", key="st_db_b"):
            fd, path = tempfile.mkstemp(suffix=".db"); os.close(fd)
            open(path, "wb").write(f.getvalue())
            eng = create_engine(f"sqlite:///{path}")
            tables = inspect(eng).get_table_names()
            st.session_state.studio = {"engine": eng, "tables": tables, "path": path, "source": f.name}
            st.success(f"已连接：{len(tables)} 张表 → {', '.join(tables)}")
    elif src == "数据库连接(URI)":
        preset = st.selectbox("预设模板", ["PostgreSQL", "MySQL", "SQL Server", "SQLite"])
        templates = {"PostgreSQL": "postgresql+psycopg2://user:password@host:5432/dbname",
                     "MySQL": "mysql+pymysql://user:password@host:3306/dbname",
                     "SQL Server": "mssql+pyodbc://user:password@host/dbname?driver=ODBC+Driver+17+for+SQL+Server",
                     "SQLite": "sqlite:///./path/to.db"}
        uri = st.text_input("连接串 (URI)", value=templates[preset], key="st_uri")
        if st.button("🔗 测试并连接", key="st_uri_b"):
            try:
                eng = create_engine(uri)
                with eng.connect():
                    tables = inspect(eng).get_table_names()
                st.session_state.studio = {"engine": eng, "tables": tables, "path": None, "source": uri}
                st.success(f"连接成功：{len(tables)} 张表")
            except Exception as e:
                st.error(f"连接失败：{e}\n若提示缺少驱动，请先安装：PostgreSQL→psycopg2-binary，MySQL→pymysql，SQL Server→pyodbc")
    else:
        if st.button("🔗 加载内置电商库", key="st_demo_b"):
            db = os.path.join(BASE, "ecommerce-sales-dashboard", "ecommerce.db")
            eng = create_engine(f"sqlite:///{db}")
            tables = inspect(eng).get_table_names()
            st.session_state.studio = {"engine": eng, "tables": tables, "path": db, "source": "内置电商库"}
            st.success(f"已加载内置库：{len(tables)} 张表 → {', '.join(tables)}")

    # ---------- 连接后：分析区 ----------
    if "studio" in st.session_state:
        eng = st.session_state.studio["engine"]
        tables = st.session_state.studio["tables"]
        st.divider()
        if st.button("⏏ 断开并重连", key="st_disc"):
            st.session_state.pop("studio", None); st.session_state.pop("studio_sql", None)
            st.session_state.pop("studio_cur", None); st.rerun()

        tbl = st.selectbox("② 选择数据表", tables, key="st_tbl")
        if st.button("加载到分析区", key="st_load"):
            st.session_state.studio_cur = pd.read_sql(text(f'SELECT * FROM "{tbl}"'), eng)
            st.session_state.studio_cur_name = tbl

        c_prev, c_prof = st.columns([2, 1])
        with c_prev:
            if "studio_cur" in st.session_state:
                st.dataframe(st.session_state.studio_cur.head(500), use_container_width=True, height=300)
        with c_prof:
            if "studio_cur" in st.session_state:
                d = st.session_state.studio_cur
                info = pd.DataFrame({"列": d.columns, "类型": d.dtypes.astype(str),
                                     "缺失%": (d.isna().mean() * 100).round(1).values,
                                     "唯一值": [int(d[c].nunique()) for c in d.columns]})
                st.markdown("**数据画像**")
                st.dataframe(info, use_container_width=True, height=300)

        # SQL Lab
        sec("③ SQL 查询（SQL Lab · 借鉴 Apache Superset）")
        default_sql = f"SELECT * FROM \"{tbl}\" LIMIT 100"
        sql = st.text_area("编写 SQL", value=default_sql, key="st_sql", height=110)
        if st.button("▶ 运行 SQL", key="st_runsql"):
            try:
                res = pd.read_sql(text(sql), eng)
                st.session_state.studio_sql = res
                st.success(f"返回 {res.shape[0]} 行 × {res.shape[1]} 列")
            except Exception as e:
                st.error(f"SQL 错误：{e}")
        if "studio_sql" in st.session_state:
            st.dataframe(st.session_state.studio_sql.head(500), use_container_width=True, height=240)

        # 交互式可视化（Power BI 风格字段面板）
        sec("④ 交互式可视化（把字段拖到 轴 / 图例 / 值）")
        src_opts = ["已选数据表"]
        if "studio_sql" in st.session_state:
            src_opts.append("SQL 查询结果")
        src_df_choice = st.radio("分析对象", src_opts, key="st_src", horizontal=True)
        df_for_chart = None
        if src_df_choice == "已选数据表" and "studio_cur" in st.session_state:
            df_for_chart = st.session_state.studio_cur
        elif src_df_choice.startswith("SQL") and "studio_sql" in st.session_state:
            df_for_chart = st.session_state.studio_sql

        if df_for_chart is not None and not df_for_chart.empty:
            ch_type = st.selectbox("图表类型", ["柱状图", "折线图", "面积图", "散点图", "饼图", "箱线图", "直方图", "热力图(相关性)"],
                                   key="st_ct")
            cols = list(df_for_chart.columns)
            nums = df_for_chart.select_dtypes(include=[np.number]).columns.tolist()
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                x = st.selectbox("X 轴 / 类别", cols, key="st_x")
            with c2:
                y = st.selectbox("Y 轴 / 值", nums if nums else cols, key="st_y")
            with c3:
                agg = st.selectbox("聚合方式", ["无(明细)", "sum", "mean", "count", "median", "min", "max"], key="st_agg")
            with c4:
                color = st.selectbox("颜色 / 分组", ["无"] + cols, key="st_color")
            title = st.text_input("图表标题", value=f"{y} by {x}", key="st_title")
            try:
                fig = _chart_from_spec(df_for_chart, ch_type, x, y, agg, color, title)
                chart_card(fig)
            except Exception as e:
                st.error(f"绘图失败：{e}")
        else:
            st.info("请先「加载数据表」或「运行 SQL」以选择分析对象。")


# ---------------- 导航 ----------------

PROJECTS = {
    "1. 电商销售看板": ("ecommerce-sales-dashboard", "SQLite + SQL + Streamlit 交互看板", "order_id, customer_id, product_id, quantity, order_date, country, price [product_name] [category]", render_sales),
    "2. 电商 SQL+BI 流水线": ("ecommerce-sql-bi-pipeline", "Python + SQL + 导出 Power BI 数据集", "order_id, customer_id, state, order_date, status, category, price, freight, total", render_sql_bi),
    "3. RFM 客户分层": ("rfm-customer-segmentation", "RFM 模型 + 客户价值分层", "invoice_no, customer_id, invoice_date, quantity, unit_price [country]", render_rfm),
    "4. K-Means 客户聚类": ("kmeans-customer-clustering", "K-Means 无监督分群 + PCA", "invoice_no, customer_id, invoice_date, quantity, unit_price", render_kmeans),
    "5. 供应链需求预测": ("supply-chain-forecasting", "需求预测 + 补货决策", "date, product_id, demand, inventory, price", render_supply),
    "6. 库存 LSTM 预测": ("inventory-lstm-forecasting", "时序预测 + 缺货预警", "date, product_id, sales, price", render_lstm),
    "7. KPI 异常检测": ("kpi-anomaly-detection", "统计异常检测 + 预警", "date, revenue, orders, traffic", render_kpi),
    "8. 亚马逊竞品分析": ("amazon-competitor-analysis", "竞品 BSR/价格/评论洞察", "date, asin, name, bsr, price, reviews, rating", render_amazon),
}

sel = render_nav()
if sel == "STUDIO":
    render_studio()
    st.stop()

name = sel
folder, desc, schema, fn = PROJECTS[name]
app_topbar(name, desc)
sec("数据接入", f"上传 CSV 表头需包含：`{schema}`")
uploaded = st.file_uploader("上传你的 CSV（留空则运行示例）", type=["csv"], key=f"up_{folder}")
col_run, col_info = st.columns([1, 3])
with col_run:
    run = st.button("▶ 运行内置示例", use_container_width=True)
with col_info:
    st.info("提示：上传 CSV 后立即分析；点「运行内置示例」会生成模拟数据并跑同样的分析逻辑。")

if run:
    with st.spinner("生成示例数据…"):
        run_demo(folder)
    st.success("示例数据已生成 ✅")

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        st.success(f"已读取上传数据：{df.shape[0]} 行 × {df.shape[1]} 列")
        fn(df)
    except Exception as e:
        st.error(f"分析出错：{e}")
elif run:
    fn(load_raw(folder))
else:
    st.info("👆 上传 CSV 或点击「运行内置示例」开始分析。")
