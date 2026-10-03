import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Customers & Marketing - ActiveShop", page_icon="👥", layout="wide")

sns.set_theme(style="whitegrid")

st.title("👥 Customers & Marketing Performance Analytics")

# Check session state data
if "orders" not in st.session_state or "customers" not in st.session_state or "sessions" not in st.session_state:
    st.warning("Data not loaded. Please return to the main Home page first.")
    st.stop()

# Retrieve clean datasets
orders = st.session_state["orders"]
customers = st.session_state["customers"]
sessions = st.session_state["sessions"]

# Filter delivered orders
delivered_orders = orders[orders["status"] == "delivered"].copy()

# Row 1: Top Customers Leaderboard & Marketing Channel Conversion
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Customers by Lifetime Value (LTV)")
    cust_spend = delivered_orders.groupby("customer_id")["order_amount"].agg(
        Total_Spent="sum",
        Orders_Count="count"
    ).reset_index()
    
    # Merge with clean customers schema
    top_cust = cust_spend.merge(customers, on="customer_id")
    top_cust = top_cust.sort_values(by="Total_Spent", ascending=False).head(10)
    
    top_cust_display = top_cust.copy()
    top_cust_display["Total Spent ($)"] = top_cust_display["Total_Spent"].map("${:,.2f}".format)
    top_cust_display = top_cust_display.rename(columns={
        "customer_id": "Customer ID", 
        "Orders_Count": "Orders",
        "region": "Region",
        "gender": "Gender",
        "age": "Age"
    })
    
    display_cols = ["Customer ID", "Region", "Gender", "Age", "Orders", "Total Spent ($)"]
    st.dataframe(top_cust_display[display_cols], use_container_width=True, hide_index=True)

with col2:
    st.subheader("Conversion Rate by Marketing Channel")
    channel_perf = sessions.groupby("channel").agg(
        total_sessions=("session_id", "count"),
        conversions=("converted", "sum")
    ).reset_index()
    channel_perf["cvr"] = (channel_perf["conversions"] / channel_perf["total_sessions"]) * 100
    channel_perf = channel_perf.sort_values(by="cvr", ascending=False)
    
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    bars2 = ax2.bar(channel_perf["channel"], channel_perf["cvr"], color="#d62728", alpha=0.85, edgecolor="black")
    ax2.set_ylabel("Conversion Rate (%)")
    plt.xticks(rotation=30, fontsize=8)
    
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.8, f"{yval:.1f}%", ha="center", va="bottom", fontsize=8, fontweight="bold")
    
    ax2.set_ylim(0, 48)
    plt.tight_layout()
    st.pyplot(fig2)

st.markdown("---")

# Row 2: Customer Loyalty Segmentation & Promo Code Usage
col3, col4 = st.columns(2)

with col3:
    st.subheader("Customer Segment Share (New vs. Loyal)")
    # Classify customers based on order frequency
    cust_orders_count = delivered_orders.groupby("customer_id")["order_id"].nunique().reset_index()
    cust_orders_count["Segment"] = cust_orders_count["order_id"].apply(
        lambda x: "One-time Customer" if x == 1 else ("Loyal (2-3 Orders)" if x <= 3 else "VIP (4+ Orders)")
    )
    segment_dist = cust_orders_count["Segment"].value_counts().reset_index()
    
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    ax3.pie(segment_dist["count"], labels=segment_dist["Segment"], autopct="%1.1f%%", startangle=140, colors=["#1f77b4", "#ff7f0e", "#2ca02c"])
    ax3.set_title("Customer Loyalty Distribution")
    plt.tight_layout()
    st.pyplot(fig3)

with col4:
    st.subheader("Promo Code Usage Breakdown")
    # Correct handling of NONE and NaN values as No Promo
    delivered_orders["promo_clean"] = delivered_orders["promo_code"].apply(
        lambda x: "No Promo" if pd.isna(x) or str(x).strip().upper() == "NONE" else str(x)
    )
    
    promo_perf = delivered_orders["promo_clean"].value_counts().reset_index()
    
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    bars4 = ax4.bar(promo_perf["promo_clean"], promo_perf["count"], color="#8c564b", alpha=0.85, edgecolor="black")
    ax4.set_ylabel("Number of Orders")
    plt.xticks(rotation=30, fontsize=8)
    
    for bar in bars4:
        yval = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2.0, yval + 30, f"{yval:,}", ha="center", va="bottom", fontsize=8, fontweight="bold")
    
    ax4.set_ylim(0, promo_perf["count"].max() * 1.15)
    plt.tight_layout()
    st.pyplot(fig4)