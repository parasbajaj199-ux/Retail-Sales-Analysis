import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Retail Sales Analytics",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 Retail Sales Analytics Dashboard")
st.caption("Python | Pandas | NumPy | Matplotlib | Seaborn")


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():

    df = pd.read_csv("python_data_analyst_sales_project.csv")

    # Duplicate removal
    df = df.drop_duplicates(keep="first")

    # Text cleaning
    text_columns = [
        "Category",
        "Region",
        "Product",
        "Segment",
        "Payment_Mode"
    ]

    for col in text_columns:
        df[col] = (
            df[col]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .str.title()
        )

    # Date cleaning
    df["Order_Date"] = pd.to_datetime(
        df["Order_Date"],
        errors="coerce"
    )

    # Numeric columns
    numeric_columns = [
        "Quantity",
        "Unit_Price",
        "Discount",
        "Sales",
        "Profit",
        "Shipping_Days"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # Missing numeric values
    df["Unit_Price"] = df["Unit_Price"].fillna(
        df["Unit_Price"].median()
    )

    df["Sales"] = df["Sales"].fillna(
        df["Sales"].median()
    )

    df["Profit"] = df["Profit"].fillna(
        df["Profit"].median()
    )

    df["Quantity"] = df["Quantity"].fillna(1)
    df["Quantity"] = df["Quantity"].replace(0, 1)

    # Date features
    df["Year"] = df["Order_Date"].dt.year
    df["Month_Number"] = df["Order_Date"].dt.month
    df["Month_Name"] = df["Order_Date"].dt.month_name()
    df["Quarter"] = (
        "Q" + df["Order_Date"].dt.quarter.astype("Int64").astype(str)
    )

    # NumPy features
    df["Profit_Margin"] = np.where(
        df["Sales"] != 0,
        (df["Profit"] / df["Sales"]) * 100,
        0
    )

    df["Sales_Category"] = np.where(
        df["Sales"] > 5000,
        "High",
        "Low"
    )

    return df


df = load_data()


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔎 Dashboard Filters")

years = sorted(
    df["Year"].dropna().unique().tolist()
)

selected_years = st.sidebar.multiselect(
    "Year",
    years,
    default=years
)

regions = sorted(df["Region"].unique())

selected_regions = st.sidebar.multiselect(
    "Region",
    regions,
    default=regions
)

categories = sorted(df["Category"].unique())

selected_categories = st.sidebar.multiselect(
    "Category",
    categories,
    default=categories
)

segments = sorted(df["Segment"].unique())

selected_segments = st.sidebar.multiselect(
    "Segment",
    segments,
    default=segments
)


# --------------------------------------------------

# FILTER DATA
# --------------------------------------------------
filtered_df = df[
    df["Year"].isin(selected_years)
    & df["Region"].isin(selected_regions)
    & df["Category"].isin(selected_categories)
    & df["Segment"].isin(selected_segments)
].copy()

# --------------------------------------------------
# KPI SECTION
# --------------------------------------------------
st.subheader("📊 Key Performance Indicators")

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_quantity = filtered_df["Quantity"].sum()
average_sales = filtered_df["Sales"].mean()

if total_sales != 0:
    profit_margin = (total_profit / total_sales) * 100
else:
    profit_margin = 0


col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Sales",
    f"₹{total_sales:,.0f}"
)

col2.metric(
    "Total Profit",
    f"₹{total_profit:,.0f}"
)

col3.metric(
    "Total Quantity",
    f"{total_quantity:,.0f}"
)

col4.metric(
    "Average Sales",
    f"₹{average_sales:,.0f}"
)

col5.metric(
    "Profit Margin",
    f"{profit_margin:.2f}%"
)


st.divider()


# --------------------------------------------------
# --------------------------------------------------
# MONTHLY SALES TREND
# --------------------------------------------------
st.subheader("📈 Monthly Sales Trend")

if not filtered_df.empty:

    monthly_sales = (
        filtered_df
        .assign(
            Year_Month=filtered_df["Order_Date"].dt.strftime("%Y-%m")
        )
        .groupby("Year_Month")["Sales"]
        .sum()
        .reset_index()
    )

    monthly_sales = monthly_sales.set_index("Year_Month")

    st.line_chart(monthly_sales)

else:
    st.warning("No data available for selected filters.")



# --------------------------------------------------
# --------------------------------------------------
# CATEGORY & REGION
# --------------------------------------------------
col1, col2 = st.columns(2)


with col1:

    st.subheader("🛍️ Sales by Category")

    category_sales = (
        filtered_df
        .groupby("Category")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(category_sales)


with col2:

    st.subheader("🌎 Sales by Region")

    region_sales = (
        filtered_df
        .groupby("Region")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(region_sales) 
# --------------------------------------------------
# PROFIT ANALYSIS
# --------------------------------------------------
col1, col2 = st.columns(2)


with col1:

    st.subheader("💰 Profit by Category")

    category_profit = (
        filtered_df
        .groupby("Category")["Profit"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(category_profit)


with col2:

    st.subheader("👥 Sales by Segment")

    segment_sales = (
        filtered_df
        .groupby("Segment")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(segment_sales)


# --------------------------------------------------
# PAYMENT MODE
# --------------------------------------------------
st.subheader("💳 Sales by Payment Mode")

payment_sales = (
    filtered_df
    .groupby("Payment_Mode")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(payment_sales)


# --------------------------------------------------
# TOP PRODUCTS
# --------------------------------------------------
st.subheader("🏆 Top 10 Products by Sales")

top_products = (
    filtered_df
    .groupby("Product")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(top_products)


# --------------------------------------------------
# --------------------------------------------------
# SALES VS PROFIT
# --------------------------------------------------
st.subheader("📌 Sales vs Profit")

if not filtered_df.empty:

    sales_profit = (
        filtered_df
        .groupby("Category")[["Sales", "Profit"]]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    st.bar_chart(sales_profit)

else:
    st.warning("No data available for selected filters.")
# ------------------------------------------------
# --------------------------------------------------
# CORRELATION HEATMAP
# --------------------------------------------------
st.subheader("🔥 Correlation Heatmap")

if not filtered_df.empty:

    correlation_data = filtered_df[
        [
            "Quantity",
            "Unit_Price",
            "Discount",
            "Sales",
            "Profit",
            "Shipping_Days"
        ]
    ].corr()

    fig, ax = plt.subplots(figsize=(8, 5))

    sns.heatmap(
        correlation_data,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        ax=ax
    )

    ax.set_title("Correlation Heatmap")

    plt.tight_layout()

    st.pyplot(fig)

else:
    st.warning("No data available for selected filters.")
# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------
st.subheader("💡 Business Insights")

if not filtered_df.empty:

    highest_sales_region = (
        filtered_df
        .groupby("Region")["Sales"]
        .sum()
        .idxmax()
    )

    highest_profit_category = (
        filtered_df
        .groupby("Category")["Profit"]
        .sum()
        .idxmax()
    )

    top_product = (
        filtered_df
        .groupby("Product")["Sales"]
        .sum()
        .idxmax()
    )

    st.write(
        f"• **Highest Sales Region:** {highest_sales_region}"
    )

    st.write(
        f"• **Highest Profit Category:** {highest_profit_category}"
    )

    st.write(
        f"• **Top Product by Sales:** {top_product}"
    )

    st.write(
        f"• **Overall Profit Margin:** {profit_margin:.2f}%"
    )


# --------------------------------------------------
# DATA PREVIEW
# --------------------------------------------------
st.subheader("📋 Filtered Data")

st.dataframe(
    filtered_df,
    use_container_width=True
)

st.caption(
    f"Showing {len(filtered_df):,} records after applying filters."
)