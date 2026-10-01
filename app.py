import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="E-Commerce Sales & Customer Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- Styling --------------------
st.markdown("""
<style>
.stApp { background: #F4F7FB; }
.block-container { max-width: 1400px; padding-top: 1.2rem; padding-bottom: 3rem; }
.hero-header {
    background: linear-gradient(135deg, #17324D 0%, #245B7A 100%);
    border-radius: 18px; padding: 1.4rem 1.8rem 1.2rem 1.8rem;
    margin-bottom: 1.1rem; box-shadow: 0 8px 24px rgba(23,50,77,0.12);
}
.hero-title { text-align:center; color:#FFFFFF; font-size:2.3rem; font-weight:800; margin:0; }
.hero-subtitle { text-align:center; color:#E7F0F6; font-size:1.02rem; margin-top:.35rem; }
.hero-caption { text-align:center; color:#C7D8E4; font-size:.85rem; margin-top:.25rem; }
.section-title { margin-top:1.1rem; margin-bottom:.6rem; color:#17324D; font-weight:750; }
[data-testid="stMetric"] {
    background:#FFFFFF; border:1px solid #DCE6EF; border-top:4px solid #3F7CAC;
    border-radius:14px; padding:.9rem 1.05rem; box-shadow:0 4px 16px rgba(23,50,77,.065);
}
[data-testid="stMetricValue"] { font-size:1.5rem; font-weight:800; color:#17324D; }
[data-testid="stMetricLabel"] { font-size:.88rem; color:#607080; }
section[data-testid="stSidebar"] { background:#F8FAFC; border-right:1px solid #DCE6EF; }
.sidebar-note { color:#687787; font-size:.82rem; line-height:1.45; }
.js-plotly-plot {
    background:#FFFFFF; border:1px solid #E0E8EF; border-radius:14px;
    padding:.15rem; box-shadow:0 3px 14px rgba(23,50,77,.045);
}
.insight-box {
    border:1px solid #DCE6EF; border-left:4px solid #3F7CAC; border-radius:12px;
    padding:.85rem 1rem; background:#FFFFFF; margin-bottom:.7rem; color:#17324D;
    box-shadow:0 3px 12px rgba(23,50,77,.04);
}
.insight-box .value { font-size:1.02rem; color:#245B7A; }
.stButton > button, .stDownloadButton > button {
    border-radius:9px; font-weight:650; border:1px solid #C9D7E3;
}
button[data-baseweb="tab"] { font-weight:650; }
[data-testid="stDataFrame"] { border:1px solid #DCE6EF; border-radius:12px; overflow:hidden; }
hr { border-color:#DCE6EF !important; }
@media (max-width:800px) { .hero-title { font-size:1.7rem; } }
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero-header">
        <div class="hero-title">📊 E-Commerce Sales & Customer Analytics</div>
        <div class="hero-subtitle">Interactive dashboard for analyzing sales, customers, products and profitability</div>
        <div class="hero-caption">Use the sidebar filters to explore performance patterns across the dataset.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- Data --------------------
@st.cache_data
def load_data():
    data = pd.read_csv("global_ecommerce_sales.csv")
    data["Order_Date"] = pd.to_datetime(data["Order_Date"])
    return data

df = load_data()
MIN_DATE, MAX_DATE = df["Order_Date"].min().date(), df["Order_Date"].max().date()

# -------------------- Sidebar filters --------------------
st.sidebar.title("🎛️ Dashboard Filters")
st.sidebar.markdown('<div class="sidebar-note">Filters update every KPI, chart and insight.</div>',
                    unsafe_allow_html=True)
st.sidebar.divider()

def reset_filters():
    for key in ("segment_filter", "region_filter", "category_filter", "payment_filter"):
        st.session_state[key] = "All"
    st.session_state["date_filter"] = (MIN_DATE, MAX_DATE)

date_range = st.sidebar.date_input("Order Date Range", value=(MIN_DATE, MAX_DATE),
                                   min_value=MIN_DATE, max_value=MAX_DATE, key="date_filter")
sel_segment = st.sidebar.selectbox("Customer Segment",
    ["All"] + sorted(df["Customer_Segment"].unique().tolist()), key="segment_filter")
sel_region = st.sidebar.selectbox("Region",
    ["All"] + sorted(df["Region"].unique().tolist()), key="region_filter")
sel_category = st.sidebar.selectbox("Product Category",
    ["All"] + sorted(df["Product_Category"].unique().tolist()), key="category_filter")
sel_payment = st.sidebar.selectbox("Payment Method",
    ["All"] + sorted(df["Payment_Method"].unique().tolist()), key="payment_filter")
st.sidebar.button("🔄 Reset Filters", on_click=reset_filters, use_container_width=True)

# Non-date filters first (reused for the previous-period comparison)
base_df = df
if sel_segment != "All":
    base_df = base_df[base_df["Customer_Segment"] == sel_segment]
if sel_region != "All":
    base_df = base_df[base_df["Region"] == sel_region]
if sel_category != "All":
    base_df = base_df[base_df["Product_Category"] == sel_category]
if sel_payment != "All":
    base_df = base_df[base_df["Payment_Method"] == sel_payment]

# date_input returns a 1-item tuple while the user is still picking the end date
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = pd.Timestamp(MIN_DATE), pd.Timestamp(MAX_DATE)

filtered_df = base_df[(base_df["Order_Date"] >= start) & (base_df["Order_Date"] <= end + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))]

# Previous period of equal length, immediately before the selected range
span = (end - start) + pd.Timedelta(days=1)
prev_df = base_df[(base_df["Order_Date"] >= start - span) & (base_df["Order_Date"] < start)]

if filtered_df.empty:
    st.warning("No records match the selected filters. Try widening the date range or resetting filters.")
    st.stop()

# -------------------- Chart helpers --------------------
BASE, ACCENT, SOFT = "#3F7CAC", "#245B7A", "#6FA4C0"
PALETTE = ["#245B7A", "#3F7CAC", "#6FA4C0", "#9CC5D9", "#17324D", "#C7D8E4"]

def show(fig, height=340):
    fig.update_layout(
        height=height, margin=dict(l=15, r=15, t=55, b=25),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13, color="#44515E"), title_font=dict(size=17, color="#17324D"),
        hoverlabel=dict(font_size=12, bgcolor="#17324D", font_color="#FFFFFF"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#D8E0E7")
    fig.update_yaxes(gridcolor="#E9EEF3", zeroline=False)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def hbar(data, x, y, title, color, height=350, money=True):
    fig = px.bar(data, x=x, y=y, orientation="h", title=title,
                 text_auto=".2s", color_discrete_sequence=[color])
    if money:
        fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    show(fig, height)

def delta_text(curr, prev):
    if prev_df.empty or not prev:
        return None
    return f"{(curr - prev) / abs(prev) * 100:+.1f}% vs prev. period"

# -------------------- KPIs --------------------
orders, sales, profit = len(filtered_df), filtered_df["Total_Sales"].sum(), filtered_df["Profit"].sum()
aov = sales / orders
margin = profit / sales * 100 if sales else 0

p_orders, p_sales, p_profit = len(prev_df), prev_df["Total_Sales"].sum(), prev_df["Profit"].sum()
p_aov = p_sales / p_orders if p_orders else 0

k1, k2, k3, k4, k5 = st.columns(5, gap="medium")
k1.metric("🛒 Total Orders", f"{orders:,}", delta_text(orders, p_orders))
k2.metric("💰 Total Sales", f"${sales:,.0f}", delta_text(sales, p_sales))
k3.metric("📈 Total Profit", f"${profit:,.0f}", delta_text(profit, p_profit))
k4.metric("🧾 Avg Order Value", f"${aov:,.2f}", delta_text(aov, p_aov))
k5.metric("📊 Profit Margin", f"{margin:.1f}%")

# -------------------- Tabs --------------------
tab_overview, tab_cust, tab_prod, tab_deep, tab_data = st.tabs(
    ["🏠 Overview", "👥 Customers & Regions", "🏆 Products", "🔎 Deep Dive", "📋 Data"])

# ===== Overview =====
with tab_overview:
    st.markdown('<h3 class="section-title">💡 Key Insights</h3>', unsafe_allow_html=True)

    def top_item(col, metric):
        grouped = filtered_df.groupby(col)[metric].sum()
        total = grouped.sum()
        return grouped.idxmax(), grouped.max(), (grouped.max() / total * 100 if total else 0)

    def insight(title, item, of_what):
        name, val, share = item
        return (f'<div class="insight-box"><b>{title}</b><br>'
                f'<span class="value">{name} — ${val:,.0f} ({share:.1f}% of {of_what})</span></div>')

    i1, i2 = st.columns(2, gap="large")
    with i1:
        st.markdown(insight("🏆 Highest Sales Category", top_item("Product_Category", "Total_Sales"), "sales"),
                    unsafe_allow_html=True)
        st.markdown(insight("🌍 Highest Sales Region", top_item("Region", "Total_Sales"), "sales"),
                    unsafe_allow_html=True)
    with i2:
        st.markdown(insight("👥 Highest Sales Segment", top_item("Customer_Segment", "Total_Sales"), "sales"),
                    unsafe_allow_html=True)
        st.markdown(insight("📈 Most Profitable Category", top_item("Product_Category", "Profit"), "profit"),
                    unsafe_allow_html=True)

    loss_orders = (filtered_df["Profit"] < 0).sum()
    if loss_orders:
        st.warning(f"⚠️ {loss_orders:,} orders ({loss_orders / orders * 100:.1f}%) made a loss, "
                   f"totalling ${filtered_df.loc[filtered_df['Profit'] < 0, 'Profit'].sum():,.0f}. "
                   "See the Deep Dive tab for the discount impact.")

    monthly = (filtered_df.groupby(filtered_df["Order_Date"].dt.to_period("M"))[["Total_Sales", "Profit"]]
               .sum().reset_index())
    monthly["Order_Date"] = monthly["Order_Date"].astype(str)
    monthly = monthly.melt("Order_Date", var_name="Metric", value_name="Amount")
    fig = px.line(monthly, x="Order_Date", y="Amount", color="Metric", markers=True,
                  title="Monthly Sales & Profit", color_discrete_sequence=[ACCENT, SOFT])
    fig.update_traces(line_width=3, marker_size=7)
    fig.update_xaxes(title=None)
    fig.update_yaxes(tickprefix="$", tickformat=",.0f", title=None)
    show(fig, 390)

# ===== Customers & Regions =====
with tab_cust:
    c1, c2 = st.columns(2, gap="large")
    with c1:
        seg_orders = filtered_df["Customer_Segment"].value_counts().reset_index()
        seg_orders.columns = ["Customer Segment", "Orders"]
        fig = px.bar(seg_orders, x="Customer Segment", y="Orders", text="Orders",
                     title="Orders by Customer Segment", color_discrete_sequence=[BASE])
        fig.update_traces(textposition="outside")
        show(fig)
    with c2:
        seg_sales = (filtered_df.groupby("Customer_Segment", as_index=False)["Total_Sales"].sum()
                     .sort_values("Total_Sales", ascending=False))
        fig = px.bar(seg_sales, x="Customer_Segment", y="Total_Sales", text_auto=".2s",
                     title="Sales by Customer Segment", color_discrete_sequence=[ACCENT])
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        show(fig)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        reg_sales = (filtered_df.groupby("Region", as_index=False)["Total_Sales"].sum()
                     .sort_values("Total_Sales"))
        hbar(reg_sales, "Total_Sales", "Region", "Sales by Region", BASE)
    with c2:
        pay_orders = filtered_df["Payment_Method"].value_counts().reset_index()
        pay_orders.columns = ["Payment Method", "Orders"]
        fig = px.bar(pay_orders.sort_values("Orders"), x="Orders", y="Payment Method", orientation="h",
                     text="Orders", title="Orders by Payment Method", color_discrete_sequence=[SOFT])
        fig.update_traces(textposition="outside")
        show(fig, 350)

    heat = filtered_df.pivot_table(index="Region", columns="Product_Category",
                                   values="Total_Sales", aggfunc="sum", fill_value=0)
    fig = px.imshow(heat, text_auto=".2s", aspect="auto", title="Sales Heatmap: Region × Product Category",
                    color_continuous_scale=["#EAF2F8", "#3F7CAC", "#17324D"])
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    fig.update_layout(coloraxis_showscale=False)
    show(fig, 380)

# ===== Products =====
with tab_prod:
    c1, c2 = st.columns(2, gap="large")
    with c1:
        cat_sales = (filtered_df.groupby("Product_Category", as_index=False)["Total_Sales"].sum()
                     .sort_values("Total_Sales"))
        hbar(cat_sales, "Total_Sales", "Product_Category", "Sales by Product Category", BASE)
    with c2:
        cat_profit = (filtered_df.groupby("Product_Category", as_index=False)["Profit"].sum()
                      .sort_values("Profit"))
        hbar(cat_profit, "Profit", "Product_Category", "Profit by Product Category", ACCENT)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        top_sales = (filtered_df.groupby("Product_Name", as_index=False)["Total_Sales"].sum()
                     .nlargest(10, "Total_Sales").sort_values("Total_Sales"))
        hbar(top_sales, "Total_Sales", "Product_Name", "Top 10 Products by Sales", BASE, 430)
    with c2:
        top_profit = (filtered_df.groupby("Product_Name", as_index=False)["Profit"].sum()
                      .nlargest(10, "Profit").sort_values("Profit"))
        hbar(top_profit, "Profit", "Product_Name", "Top 10 Products by Profit", ACCENT, 430)

    worst = (filtered_df.groupby("Product_Name", as_index=False)["Profit"].sum()
             .nsmallest(10, "Profit").sort_values("Profit", ascending=False))
    hbar(worst, "Profit", "Product_Name", "Bottom 10 Products by Profit (loss-makers first)", "#B5483B", 430)

# ===== Deep Dive =====
with tab_deep:
    c1, c2 = st.columns(2, gap="large")
    with c1:
        fig = px.scatter(filtered_df, x="Total_Sales", y="Profit", color="Customer_Segment",
                         opacity=0.65, title="Sales vs Profit by Segment", color_discrete_sequence=PALETTE)
        fig.update_xaxes(tickprefix="$", tickformat=",.0f")
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        show(fig, 390)
    with c2:
        disc = filtered_df.groupby("Discount_Percent", as_index=False)["Profit"].mean()
        fig = px.bar(disc, x="Discount_Percent", y="Profit", text_auto=".0f",
                     title="Average Profit per Order by Discount Level", color_discrete_sequence=[ACCENT])
        fig.update_xaxes(title="Discount (%)", ticksuffix="%")
        fig.update_yaxes(tickprefix="$", tickformat=",.0f")
        show(fig, 390)

    corr_cols = [c for c in ["Quantity", "Discount_Percent", "Total_Sales", "Profit"] if c in filtered_df.columns]
    corr = filtered_df[corr_cols].corr().round(2)
    fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Between Key Metrics",
                    color_continuous_scale=["#B5483B", "#FFFFFF", "#245B7A"], zmin=-1, zmax=1)
    show(fig, 380)

# ===== Data =====
with tab_data:
    st.write(f"Showing **{len(filtered_df):,} records** based on the selected filters.")
    st.dataframe(filtered_df, use_container_width=True, height=420)
    st.download_button("⬇️ Download Filtered Data",
                       data=filtered_df.to_csv(index=False).encode("utf-8"),
                       file_name="filtered_ecommerce_data.csv", mime="text/csv")
    st.markdown("---")
    st.markdown(
        "**About:** Built for the Fundamentals of Data Science project using Python, Pandas, "
        "Plotly and Streamlit. KPI changes compare the selected date range with the equal-length "
        "period immediately before it."
    )
