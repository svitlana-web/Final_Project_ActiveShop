import os
import pandas as pd
import streamlit as st

# Set page layout and configuration
st.set_page_config(
    page_title="ActiveShop Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cached function to load all clean datasets
@st.cache_data
def load_all_data():
    base_paths = [
        "../data",
        "data",
        os.path.join(os.path.dirname(__file__), "..", "data"),
        os.path.join(os.path.dirname(__file__), "data")
    ]
    
    def find_and_read(filename):
        for base in base_paths:
            full_path = os.path.abspath(os.path.join(base, filename))
            if os.path.exists(full_path):
                return pd.read_csv(full_path)
        raise FileNotFoundError(f"File {filename} not found in path options.")

    customers = find_and_read("customers_clean.csv")
    orders = find_and_read("orders_clean.csv")
    order_items = find_and_read("order_items_clean.csv")
    products = find_and_read("products_clean.csv")
    sessions = find_and_read("sessions_clean.csv")
    
    # Pre-process datetime columns
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    customers["signup_date"] = pd.to_datetime(customers["signup_date"])
    sessions["session_start"] = pd.to_datetime(sessions["session_start"])
    
    return customers, orders, order_items, products, sessions

# Load data into session state
try:
    customers, orders, order_items, products, sessions = load_all_data()
    st.session_state["customers"] = customers
    st.session_state["orders"] = orders
    st.session_state["order_items"] = order_items
    st.session_state["products"] = products
    st.session_state["sessions"] = sessions
except Exception as e:
    st.error(f"Error loading datasets: {e}")

# Landing Home Page UI
st.title("🛒 ActiveShop Business Analytics Portal")
st.markdown("""
Welcome to the **ActiveShop** executive analytics portal!

Use the **sidebar menu** on the left to navigate through the project pages:
* **1. Overview:** High-level KPIs and business metric filters.
* **2. Sales:** Monthly trends, category performance, top products, and regional sales.
* **3. Customers & Marketing:** Customer leaderboards, marketing channel conversion, loyalty levels, and promo usage.
* **4. A/B Test:** Checkout layout experiment results, statistical testing, and deployment decisions.
""")

st.info("👈 Select a page from the left sidebar to start exploring.")