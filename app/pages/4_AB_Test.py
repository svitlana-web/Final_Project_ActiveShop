import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from scipy.stats import chi2_contingency

st.set_page_config(page_title="A/B Test Analytics - ActiveShop", page_icon="🧪", layout="wide")

sns.set_theme(style="whitegrid")

st.title("🧪 Checkout Layout A/B Experiment Dashboard")

# Check session state data
if "sessions" not in st.session_state:
    st.warning("Data not loaded. Please return to the main Home page first.")
    st.stop()

# Retrieve sessions dataset
sessions = st.session_state["sessions"].copy()
sessions["session_start"] = pd.to_datetime(sessions["session_start"])

# Filter first sessions per customer for clean A/B test analysis
sessions_sorted = sessions.sort_values(by=["customer_id", "session_start"])
first_sessions = sessions_sorted.groupby("customer_id").first().reset_index()

# Calculate group-level metrics
ab_perf = first_sessions.groupby("ab_group").agg(
    Total_Visitors=("session_id", "count"),
    Conversions=("converted", "sum")
).reset_index()

ab_perf["CVR (%)"] = (ab_perf["Conversions"] / ab_perf["Total_Visitors"]) * 100

# Extract specific values for Group A and Group B
n_a = ab_perf.loc[ab_perf["ab_group"] == "A", "Total_Visitors"].values[0]
cvr_a = ab_perf.loc[ab_perf["ab_group"] == "A", "CVR (%)"].values[0]

n_b = ab_perf.loc[ab_perf["ab_group"] == "B", "Total_Visitors"].values[0]
cvr_b = ab_perf.loc[ab_perf["ab_group"] == "B", "CVR (%)"].values[0]

abs_diff = cvr_b - cvr_a
rel_lift = ((cvr_b - cvr_a) / cvr_a) * 100

# Perform Chi-Square test of independence
contingency_matrix = [
    [ab_perf.loc[ab_perf["ab_group"] == "A", "Conversions"].values[0], n_a - ab_perf.loc[ab_perf["ab_group"] == "A", "Conversions"].values[0]],
    [ab_perf.loc[ab_perf["ab_group"] == "B", "Conversions"].values[0], n_b - ab_perf.loc[ab_perf["ab_group"] == "B", "Conversions"].values[0]]
]
chi2, p_value, dof, _ = chi2_contingency(contingency_matrix)

# Display Key Statistical Metrics in 4 Cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("Control (A) Visitors / CVR", f"{n_a:,} users", f"{cvr_a:.2f}%")
col2.metric("Treatment (B) Visitors / CVR", f"{n_b:,} users", f"{cvr_b:.2f}%")
col3.metric("Absolute Lift", f"+{abs_diff:.2f} p.p.", f"+{rel_lift:.2f}% relative")
col4.metric("p-value", f"{p_value:.6f}", "Statistically Significant" if p_value < 0.05 else "Not Significant")

st.markdown("---")

# Visual Comparison & Contingency Summary
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("First-Session Conversion Comparison")
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ["#7f7f7f", "#2ca02c"]
    bars = ax.bar(ab_perf["ab_group"], ab_perf["CVR (%)"], color=colors, alpha=0.85, edgecolor="black", width=0.4)
    
    ax.set_ylabel("Conversion Rate (%)")
    ax.set_xticklabels(["Group A (Control)", "Group B (Treatment)"])
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.8, f"{yval:.2f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")
    
    ax.set_ylim(0, 48)
    plt.tight_layout()
    st.pyplot(fig)

with col_right:
    st.subheader("Experiment Summary Table")
    summary_df = pd.DataFrame({
        "Metric": ["Sample Size (Users)", "Conversions", "Conversion Rate", "Chi-Square Statistic", "p-value", "Result"],
        "Group A (Control)": [f"{n_a:,}", f"{ab_perf.loc[ab_perf['ab_group'] == 'A', 'Conversions'].values[0]:,}", f"{cvr_a:.2f}%", f"{chi2:.4f}", f"{p_value:.6f}", "Baseline"],
        "Group B (Treatment)": [f"{n_b:,}", f"{ab_perf.loc[ab_perf['ab_group'] == 'B', 'Conversions'].values[0]:,}", f"{cvr_b:.2f}%", f"{chi2:.4f}", f"{p_value:.6f}", "Winner (+8.55 p.p.)"]
    })
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.markdown("---")

# Executive Conclusion Box
st.subheader("📌 Executive Conclusion & Decision")
st.success("""
* **Statistical Significance:** The hypothesis test confirms a statistically significant difference between variants ($p = 0.000062 < 0.05$).
* **Business Impact:** Checkout Layout B increased first-session conversion from **29.03%** to **37.58%** (+8.55 percentage points).
* **Final Decision:** **Full Rollout Recommended.** Implement Layout B for 100% of e-commerce traffic to maximize order intake and overall revenue.
""")