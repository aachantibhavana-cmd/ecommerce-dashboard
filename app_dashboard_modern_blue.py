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
    border-radius: 18px;
    padding: 1.55rem 1.8rem 1.35rem 1.8rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 8px 24px rgba(23,50,77,0.12);
}
.hero-title { text-align:center; color:#FFFFFF; font-size:2.35rem; font-weight:800; margin:0; }
.hero-subtitle { text-align:center; color:#E7F0F6; font-size:1.03rem; margin-top:.35rem; }
.hero-caption { text-align:center; color:#C7D8E4; font-size:.86rem; margin-top:.25rem; }

.section-title { margin-top:1.35rem; margin-bottom:.65rem; color:#17324D; font-weight:750; }

[data-testid="stMetric"] {
    background:#FFFFFF; border:1px solid #DCE6EF; border-top:4px solid #3F7CAC;
    border-radius:14px; padding:.9rem 1.05rem; box-shadow:0 4px 16px rgba(23,50,77,.065);
}
[data-testid="stMetricValue"] { font-size:1.75rem; font-weight:800; color:#17324D; }
[data-testid="stMetricLabel"] { font-size:.88rem; color:#607080; }

section[data-testid="stSidebar"] { background:#F8FAFC; border-right:1px solid #DCE6EF; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 { color:#17324D; }
.sidebar-note { color:#687787; font-size:.82rem; line-height:1.45; }

.js-plotly-plot {
    background:#FFFFFF; border:1px solid #E0E8EF; border-radius:14px;
    padding:.15rem; box-shadow:0 3px 14px rgba(23,50,77,.045);
}
.insight-box {
    border:1px solid #DCE6EF; border-left:4px solid #3F7CAC; border-radius:12px;
    padding:.85rem 1rem; background:#FFFFFF; margin-bottom:.7rem;
    box-shadow:0 3px 12px rgba(23,50,77,.04);
}
.stButton > button, .stDownloadButton > button {
    border-radius:9px; font-weight:650; border:1px solid #C9D7E3;
}
[data-testid="stDataFrame"] { border:1px solid #DCE6EF; border-radius:12px; overflow:hidden; }
[data-testid="stExpander"] { background:#FFFFFF; border:1px solid #DCE6EF; border-radius:13px; }
hr { border-color:#DCE6EF !important; }
@media (max-width:800px) { .hero-title { font-size:1.75rem; } }
</style>
""", unsafe_allow_html=True)

# -------------------- Header --------------------
st.markdown(
    """
    <div class="hero-header">
        <div class="hero-title">📊 E-Commerce Sales & Customer Analytics</div>
        <div class="hero-subtitle">Interactive dashboard for analyzing sales, customers, products and profitability</div>
        <div class="hero-caption">Use the filters to explore performance patterns and generate a focused view of the dataset.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- Data --------------------
df = pd.read_csv("global_ecommerce_sales.csv")
df["Order_Date"] = pd.to_datetime(df["Order_Date"])

# -------------------- Sidebar --------------------
st.sidebar.title("🎛️ Dashboard Filters")

st.sidebar.markdown(
    '<div class="sidebar-note">Choose filters to update every KPI and chart.</div>',
    unsafe_allow_html=True,
)

st.sidebar.divider()


def reset_filters():
    st.session_state["segment_filter"] = "All"
    st.session_state["region_filter"] = "All"
    st.session_state["category_filter"] = "All"
    st.session_state["payment_filter"] = "All"

selected_segment = st.sidebar.selectbox(
    "Customer Segment",
    ["All"] + sorted(df["Customer_Segment"].unique().tolist()),
    key="segment_filter",
)

selected_region = st.sidebar.selectbox(
    "Region",
    ["All"] + sorted(df["Region"].unique().tolist()),
    key="region_filter",
)

selected_category = st.sidebar.selectbox(
    "Product Category",
    ["All"] + sorted(df["Product_Category"].unique().tolist()),
    key="category_filter",
)

selected_payment = st.sidebar.selectbox(
    "Payment Method",
    ["All"] + sorted(df["Payment_Method"].unique().tolist()),
    key="payment_filter",
)

st.sidebar.button(
    "🔄 Reset Filters",
    on_click=reset_filters,
    use_container_width=True,
)


filtered_df = df.copy()

if selected_segment != "All":
    filtered_df = filtered_df[
        filtered_df["Customer_Segment"] == selected_segment
    ]

if selected_region != "All":
    filtered_df = filtered_df[
        filtered_df["Region"] == selected_region
    ]

if selected_category != "All":
    filtered_df = filtered_df[
        filtered_df["Product_Category"] == selected_category
    ]

if selected_payment != "All":
    filtered_df = filtered_df[
        filtered_df["Payment_Method"] == selected_payment
    ]


# Common chart styling
CHART_HEIGHT = 330
BASE_COLOR = "#3F7CAC"
ACCENT_COLOR = "#245B7A"
SECONDARY_COLOR = "#6FA4C0"


def style_fig(fig, height=CHART_HEIGHT):
    fig.update_layout(
        height=height,
        margin=dict(l=15, r=15, t=55, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13, color="#44515E"),
        title_font=dict(size=17, color="#17324D"),
        hoverlabel=dict(font_size=12, bgcolor="#17324D", font_color="#FFFFFF"),
    )
    fig.update_xaxes(showgrid=False, linecolor="#D8E0E7")
    fig.update_yaxes(gridcolor="#E9EEF3", zeroline=False)
    return fig


def show_chart(fig):
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

# -------------------- KPIs --------------------
st.markdown('<h2 class="section-title">📌 Key Performance Indicators</h2>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3, gap="large")
with col1:
    st.metric("🛒 Total Orders", f"{len(filtered_df):,}")
with col2:
    st.metric("💰 Total Sales", f"${filtered_df['Total_Sales'].sum():,.2f}")
with col3:
    st.metric("📈 Total Profit", f"${filtered_df['Profit'].sum():,.2f}")

st.divider()

# -------------------- Customer Overview --------------------
st.markdown('<h2 class="section-title">👥 Customer Overview</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="large")

with col1:
    segment_orders = filtered_df["Customer_Segment"].value_counts().reset_index()
    segment_orders.columns = ["Customer Segment", "Orders"]
    fig = px.bar(
        segment_orders,
        x="Customer Segment",
        y="Orders",
        title="Orders by Customer Segment",
        text="Orders",
        color_discrete_sequence=[BASE_COLOR],
    )
    fig.update_traces(textposition="outside")
    show_chart(style_fig(fig))

with col2:
    segment_sales = (
        filtered_df.groupby("Customer_Segment", as_index=False)["Total_Sales"]
        .sum()
        .sort_values("Total_Sales", ascending=False)
    )
    fig = px.bar(
        segment_sales,
        x="Customer_Segment",
        y="Total_Sales",
        title="Sales by Customer Segment",
        text_auto=".2s",
        color_discrete_sequence=[ACCENT_COLOR],
    )
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    show_chart(style_fig(fig))

# -------------------- Regional Performance --------------------
st.markdown('<h2 class="section-title">🌍 Sales & Regional Performance</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    region_orders = filtered_df["Region"].value_counts().reset_index()
    region_orders.columns = ["Region", "Orders"]
    fig = px.bar(
        region_orders.sort_values("Orders"),
        x="Orders",
        y="Region",
        orientation="h",
        title="Orders by Region",
        text="Orders",
        color_discrete_sequence=[BASE_COLOR],
    )
    fig.update_traces(textposition="outside")
    show_chart(style_fig(fig, 350))

with col2:
    category_sales = (
        filtered_df.groupby("Product_Category", as_index=False)["Total_Sales"]
        .sum()
        .sort_values("Total_Sales")
    )
    fig = px.bar(
        category_sales,
        x="Total_Sales",
        y="Product_Category",
        orientation="h",
        title="Sales by Product Category",
        text_auto=".2s",
        color_discrete_sequence=[BASE_COLOR],
    )
    fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    show_chart(style_fig(fig, 350))

# -------------------- Sales Trend --------------------
st.markdown('<h2 class="section-title">📈 Sales Trend</h2>', unsafe_allow_html=True)
monthly_sales = (
    filtered_df.groupby(filtered_df["Order_Date"].dt.to_period("M"))["Total_Sales"]
    .sum()
    .reset_index()
)
monthly_sales["Order_Date"] = monthly_sales["Order_Date"].astype(str)
fig = px.line(
    monthly_sales,
    x="Order_Date",
    y="Total_Sales",
    title="Monthly Sales",
    markers=True,
    color_discrete_sequence=[ACCENT_COLOR],
)
fig.update_traces(line_width=3, marker_size=7)
fig.update_yaxes(tickprefix="$", tickformat=",.0f")
show_chart(style_fig(fig, 390))

# -------------------- Product & Payment --------------------
st.markdown('<h2 class="section-title">🏆 Product & Payment Performance</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="large")

with col1:
    category_profit = (
        filtered_df.groupby("Product_Category", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit")
    )
    fig = px.bar(
        category_profit,
        x="Profit",
        y="Product_Category",
        orientation="h",
        title="Profit by Product Category",
        text_auto=".2s",
        color_discrete_sequence=[ACCENT_COLOR],
    )
    fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    show_chart(style_fig(fig, 350))

with col2:
    payment_orders = filtered_df["Payment_Method"].value_counts().reset_index()
    payment_orders.columns = ["Payment Method", "Orders"]
    fig = px.bar(
        payment_orders.sort_values("Orders"),
        x="Orders",
        y="Payment Method",
        orientation="h",
        title="Orders by Payment Method",
        text="Orders",
        color_discrete_sequence=[SECONDARY_COLOR],
    )
    fig.update_traces(textposition="outside")
    show_chart(style_fig(fig, 350))

# -------------------- Top Products --------------------
st.markdown('<h2 class="section-title">🥇 Top Performing Products</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="large")

with col1:
    top_products_sales = (
        filtered_df.groupby("Product_Name", as_index=False)["Total_Sales"]
        .sum()
        .sort_values("Total_Sales", ascending=False)
        .head(10)
        .sort_values("Total_Sales")
    )
    fig = px.bar(
        top_products_sales,
        x="Total_Sales",
        y="Product_Name",
        orientation="h",
        title="Top 10 Products by Sales",
        text_auto=".2s",
        color_discrete_sequence=[BASE_COLOR],
    )
    fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    show_chart(style_fig(fig, 430))

with col2:
    top_products_profit = (
        filtered_df.groupby("Product_Name", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit", ascending=False)
        .head(10)
        .sort_values("Profit")
    )
    fig = px.bar(
        top_products_profit,
        x="Profit",
        y="Product_Name",
        orientation="h",
        title="Top 10 Products by Profit",
        text_auto=".2s",
        color_discrete_sequence=[ACCENT_COLOR],
    )
    fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    show_chart(style_fig(fig, 430))

# -------------------- Relationship Analysis --------------------
st.markdown('<h2 class="section-title">🔎 Relationship Analysis</h2>', unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="large")

with col1:
    fig = px.scatter(
        filtered_df,
        x="Total_Sales",
        y="Profit",
        title="Sales vs Profit",
        opacity=0.65,
        
    )
    fig.update_xaxes(tickprefix="$", tickformat=",.0f")
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    show_chart(style_fig(fig, 390))

with col2:
    discount_profit = (
        filtered_df.groupby("Discount_Percent", as_index=False)["Profit"]
        .mean()
    )
    fig = px.line(
        discount_profit,
        x="Discount_Percent",
        y="Profit",
        title="Discount vs Average Profit",
        markers=True,
        color_discrete_sequence=[ACCENT_COLOR],
    )
    fig.update_traces(line_width=3, marker_size=8)
    fig.update_xaxes(title="Discount (%)", ticksuffix="%")
    fig.update_yaxes(tickprefix="$", tickformat=",.0f")
    show_chart(style_fig(fig, 390))

fig = px.scatter(
    filtered_df,
    x="Quantity",
    y="Total_Sales",
    title="Quantity vs Total Sales",
    opacity=0.65,
    
)
fig.update_yaxes(tickprefix="$", tickformat=",.0f")
show_chart(style_fig(fig, 390))

# -------------------- Key Insights --------------------
st.markdown('<h2 class="section-title">💡 Key Insights</h2>', unsafe_allow_html=True)

if not filtered_df.empty:

    highest_category = (
        filtered_df.groupby("Product_Category")["Total_Sales"]
        .sum()
        .idxmax()
    )

    highest_region = (
        filtered_df.groupby("Region")["Total_Sales"]
        .sum()
        .idxmax()
    )

    highest_segment = (
        filtered_df.groupby("Customer_Segment")["Total_Sales"]
        .sum()
        .idxmax()
    )

    most_profitable_category = (
        filtered_df.groupby("Product_Category")["Profit"]
        .sum()
        .idxmax()
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:

        st.markdown(
            f'<div class="insight-box"><b>🏆 Highest Sales Category</b><br>'
            f'<span style="font-size:1.05rem;color:#245B7A;">{highest_category}</span></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="insight-box"><b>🌍 Highest Sales Region</b><br>'
            f'<span style="font-size:1.05rem;color:#245B7A;">{highest_region}</span></div>',
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f'<div class="insight-box"><b>👥 Highest Sales Customer Segment</b><br>'
            f'<span style="font-size:1.05rem;color:#245B7A;">{highest_segment}</span></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="insight-box"><b>📈 Most Profitable Category</b><br>'
            f'<span style="font-size:1.05rem;color:#245B7A;">{most_profitable_category}</span></div>',
            unsafe_allow_html=True
        )

else:
    st.warning("No records match the selected filters.")

st.divider()

# -------------------- Data Explorer --------------------
st.markdown('<h2 class="section-title">📋 Data Explorer</h2>', unsafe_allow_html=True)

with st.expander("Open Data Explorer", expanded=False):
    st.write(f"Showing **{len(filtered_df):,} records** based on the selected filters.")
    st.dataframe(filtered_df, use_container_width=True, height=400)

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data",
        data=csv_data,
        file_name="filtered_ecommerce_data.csv",
        mime="text/csv",
    )

# -------------------- About --------------------
st.markdown('<h2 class="section-title">ℹ️ About This Dashboard</h2>', unsafe_allow_html=True)
st.write(
     """
        This interactive dashboard is developed as part of the Fundamentals of Data Science
        project. It analyzes e-commerce sales, customer segments, products, regions,
        payment methods and profitability using Python, Pandas and Streamlit.
    
        Use the sidebar filters to explore different parts of the dataset and observe
        how the key performance indicators and visualizations change dynamically.
    
        The dashboard converts the earlier data analysis into an interactive
        implementation that allows users to explore the dataset and download
        filtered results.
        """
    
)
