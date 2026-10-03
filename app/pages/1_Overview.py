import pandas as pd
import streamlit as st

st.set_page_config(page_title="Overview - ActiveShop", page_icon="📊", layout="wide")

# Custom CSS to adjust metric font size and avoid text truncation (...)
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
        white-space: nowrap !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Executive Overview & Key Performance Indicators")

# Check if data exists in session_state
if "orders" not in st.session_state or "customers" not in st.session_state:
    st.warning("Data not loaded. Please go back to the main Home page first.")
    st.stop()

# Retrieve clean datasets from session_state
orders = st.session_state["orders"]

# Filter strictly by delivered status for financial KPIs
delivered_orders = orders[orders["status"] == "delivered"].copy()
delivered_orders["month_year"] = delivered_orders["order_date"].dt.to_period("M").astype(str)

# Extract sorted unique months
available_months = sorted(delivered_orders["month_year"].unique())

# Month Range Filter in Sidebar
st.sidebar.header("Filter Options")

start_month, end_month = st.sidebar.select_slider(
    "Select Month Range:",
    options=available_months,
    value=(available_months[0], available_months[-1])
)

# Filter orders by selected month range
filtered_orders = delivered_orders[
    (delivered_orders["month_year"] >= start_month) & 
    (delivered_orders["month_year"] <= end_month)
]

# Calculate financial & operational KPIs
total_revenue = filtered_orders["order_amount"].sum()
total_orders_count = filtered_orders["order_id"].nunique()
avg_order_value = filtered_orders["order_amount"].mean() if total_orders_count > 0 else 0
unique_customers = filtered_orders["customer_id"].nunique()
gross_revenue = filtered_orders["gross_amount"].sum()

# Display KPI cards in 5 columns
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Revenue ($)", f"${total_revenue:,.2f}")
col2.metric("Total Orders", f"{total_orders_count:,}")
col3.metric("Average Order Value", f"${avg_order_value:,.2f}")
col4.metric("Unique Customers", f"{unique_customers:,}")
col5.metric("Gross Revenue", f"${gross_revenue:,.2f}")

st.markdown("---")

# Monthly Breakdown Table for Selected Period
st.subheader("Monthly Performance Summary")

monthly_summary = filtered_orders.groupby("month_year").agg(
    Revenue=("order_amount", "sum"),
    Orders=("order_id", "nunique"),
    AOV=("order_amount", "mean"),
    Customers=("customer_id", "nunique")
).reset_index()

monthly_summary["Revenue"] = monthly_summary["Revenue"].map("${:,.2f}".format)
monthly_summary["AOV"] = monthly_summary["AOV"].map("${:,.2f}".format)

st.dataframe(monthly_summary, use_container_width=True)