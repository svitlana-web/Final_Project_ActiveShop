import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Sales Analytics - ActiveShop", page_icon="📈", layout="wide")

# Set global visual style for seaborn
sns.set_theme(style="whitegrid")

st.title("📈 Sales & Product Performance Analytics")

# Check session state data
if "orders" not in st.session_state or "products" not in st.session_state:
    st.warning("Data not loaded. Please return to the main Home page first.")
    st.stop()

# Retrieve clean datasets
orders = st.session_state["orders"]
order_items = st.session_state["order_items"]
products = st.session_state["products"]
customers = st.session_state["customers"]

# Filter delivered orders
delivered_orders = orders[orders["status"] == "delivered"].copy()
delivered_orders["month_year"] = delivered_orders["order_date"].dt.to_period("M").astype(str)

# Sidebar Category Filter
st.sidebar.header("Filter Options")
available_categories = ["All Categories"] + sorted(products["category"].unique().tolist())
selected_category = st.sidebar.selectbox("Select Product Category:", available_categories)

# Prepare merged dataset
items_orders = order_items.merge(delivered_orders[["order_id", "month_year", "customer_id"]], on="order_id")
merged_sales = items_orders.merge(products, on="product_id")

if selected_category != "All Categories":
    merged_sales = merged_sales[merged_sales["category"] == selected_category]
    filtered_delivered_ids = merged_sales["order_id"].unique()
    filtered_orders = delivered_orders[delivered_orders["order_id"].isin(filtered_delivered_ids)]
else:
    filtered_orders = delivered_orders

# Row 1: Revenue Trend & Category Performance
col1, col2 = st.columns(2)

with col1:
    st.subheader("Monthly Revenue Trend")
    monthly_rev = filtered_orders.groupby("month_year")["order_amount"].sum().reset_index()
    
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.plot(monthly_rev["month_year"], monthly_rev["order_amount"] / 1000, marker="o", color="#1f77b4", linewidth=2)
    ax1.fill_between(monthly_rev["month_year"], monthly_rev["order_amount"] / 1000, color="#1f77b4", alpha=0.15)
    ax1.set_ylabel("Revenue ($k)")
    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()
    st.pyplot(fig1)

with col2:
    st.subheader("Gross Revenue by Category")
    cat_perf = merged_sales.groupby("category")["line_amount"].sum().reset_index().sort_values(by="line_amount", ascending=False)
    
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    bars2 = ax2.bar(cat_perf["category"], cat_perf["line_amount"] / 1000, color="#2ca02c", alpha=0.85, edgecolor="black")
    ax2.set_ylabel("Revenue ($k)")
    plt.xticks(rotation=30, fontsize=8)
    
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f"${yval:.1f}k", ha="center", va="bottom", fontsize=8, fontweight="bold")
    
    plt.tight_layout()
    st.pyplot(fig2)

st.markdown("---")

# Row 2: Top Products & Regional Distribution
col3, col4 = st.columns(2)

with col3:
    st.subheader("Top Products by Gross Revenue")
    top_prod = merged_sales.groupby("product_name")["line_amount"].sum().reset_index().sort_values(by="line_amount", ascending=False).head(5)
    
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    bars3 = ax3.barh(top_prod["product_name"][::-1], (top_prod["line_amount"] / 1000)[::-1], color="#ff7f0e", alpha=0.85, edgecolor="black")
    ax3.set_xlabel("Revenue ($k)")
    
    for bar in bars3:
        xval = bar.get_width()
        ax3.text(xval + 0.5, bar.get_y() + bar.get_height()/2.0, f"${xval:.1f}k", ha="left", va="center", fontsize=8, fontweight="bold")
    
    plt.tight_layout()
    st.pyplot(fig3)

with col4:
    st.subheader("Revenue Distribution by Region")
    orders_cust = filtered_orders.merge(customers, on="customer_id")
    region_perf = orders_cust.groupby("region")["order_amount"].sum().reset_index().sort_values(by="order_amount", ascending=False)
    
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    bars4 = ax4.bar(region_perf["region"], region_perf["order_amount"] / 1000, color="#9467bd", alpha=0.85, edgecolor="black")
    ax4.set_ylabel("Revenue ($k)")
    plt.xticks(rotation=30, fontsize=8)
    
    for bar in bars4:
        yval = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f"${yval:.1f}k", ha="center", va="bottom", fontsize=8, fontweight="bold")
    
    plt.tight_layout()
    st.pyplot(fig4)