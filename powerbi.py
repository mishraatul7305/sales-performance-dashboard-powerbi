import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="",
    layout="wide"
)

st.title("Sales Performance Dashboard")

# -----------------------------
# LOAD DATA
# -----------------------------
# Change this to your Excel/CSV file
file_path = "sales_data.xlsx"

df = pd.read_excel(file_path)

# If CSV:
# df = pd.read_csv("sales_data.csv")

# -----------------------------
# DATA PREPARATION
# -----------------------------
df["Order Date"] = pd.to_datetime(df["Order Date"])

df["Year"] = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.month_name()
df["Quarter"] = "Q" + df["Order Date"].dt.quarter.astype(str)

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

cities = st.sidebar.multiselect(
    "City",
    options=sorted(df["City"].dropna().unique()),
    default=sorted(df["City"].dropna().unique())
)

categories = st.sidebar.multiselect(
    "Product Category",
    options=sorted(df["Product Category"].dropna().unique()),
    default=sorted(df["Product Category"].dropna().unique())
)

customer_types = st.sidebar.multiselect(
    "Customer Type",
    options=sorted(df["Customer Type"].dropna().unique()),
    default=sorted(df["Customer Type"].dropna().unique())
)

filtered_df = df[
    (df["City"].isin(cities)) &
    (df["Product Category"].isin(categories)) &
    (df["Customer Type"].isin(customer_types))
]

# -----------------------------
# KPI CARDS
# -----------------------------
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_quantity = filtered_df["Quantity"].sum()
total_unit_price = filtered_df["Unit Price"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    " Total Sales",
    f"{total_sales:,.2f}"
)

col2.metric(
    "Total Profit",
    f"{total_profit:,.2f}"
)

col3.metric(
    "Total Quantity",
    f"{total_quantity:,.0f}"
)

col4.metric(
    " Unit Price",
    f"{total_unit_price:,.2f}"
)

st.divider()

# -----------------------------
# ROW 1
# -----------------------------
col1, col2 = st.columns(2)

# Product Category by Quarter
with col1:

    quarter_data = (
        filtered_df
        .groupby("Quarter")["Product Category"]
        .count()
        .reset_index(name="Count")
    )

    fig_quarter = px.pie(
        quarter_data,
        names="Quarter",
        values="Count",
        title="Count of Product Category by Quarter",
        hole=0.35
    )

    st.plotly_chart(
        fig_quarter,
        use_container_width=True
    )


# Sales / Profit / Unit Price
with col2:

    financial_data = pd.DataFrame({
        "Metric": [
            "Sales",
            "Profit",
            "Unit Price"
        ],
        "Value": [
            filtered_df["Sales"].sum(),
            filtered_df["Profit"].sum(),
            filtered_df["Unit Price"].sum()
        ]
    })

    fig_financial = px.pie(
        financial_data,
        names="Metric",
        values="Value",
        title="Sales, Profit and Unit Price",
        hole=0.55
    )

    st.plotly_chart(
        fig_financial,
        use_container_width=True
    )

# -----------------------------
# ROW 2
# -----------------------------
col1, col2 = st.columns(2)

# Payment Method
with col1:

    payment_data = (
        filtered_df
        .groupby("Payment Method")
        .agg(
            Profit=("Profit", "sum"),
            Count=("Order ID", "count")
        )
        .reset_index()
    )

    fig_payment = px.line(
        payment_data,
        x="Payment Method",
        y=["Profit", "Count"],
        markers=True,
        title="Payment Method Analysis"
    )

    st.plotly_chart(
        fig_payment,
        use_container_width=True
    )


# City vs Customer Type
with col2:

    city_customer = (
        filtered_df
        .groupby(["City", "Customer Type"])
        .size()
        .reset_index(name="Count")
    )

    fig_city = px.line(
        city_customer,
        x="City",
        y="Count",
        color="Customer Type",
        markers=True,
        title="Count of Orders by City and Customer Type"
    )

    fig_city.update_xaxes(tickangle=45)

    st.plotly_chart(
        fig_city,
        use_container_width=True
    )

# -----------------------------
# SALES BY MONTH
# -----------------------------
monthly_sales = (
    filtered_df
    .groupby(filtered_df["Order Date"].dt.to_period("M"))["Sales"]
    .sum()
    .reset_index()
)

monthly_sales["Order Date"] = (
    monthly_sales["Order Date"]
    .astype(str)
)

fig_month = px.line(
    monthly_sales,
    x="Order Date",
    y="Sales",
    markers=True,
    title="Monthly Sales Trend"
)

st.plotly_chart(
    fig_month,
    use_container_width=True
)

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("Order Details")

display_columns = [
    "Order ID",
    "Order Date",
    "City",
    "Product Category",
    "Payment Method",
    "Customer Type",
    "Quantity",
    "Unit Price",
    "Sales",
    "Profit"
]

# Show only columns that actually exist
display_columns = [
    col for col in display_columns
    if col in filtered_df.columns
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True,
    height=400
)