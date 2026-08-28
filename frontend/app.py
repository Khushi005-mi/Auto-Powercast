import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from models.predictor import PowercastPredictor

st.set_page_config(page_title="Auto-Powercast AI | Energy Infrastructure Intelligence", page_icon="⚡", layout="wide")

@st.cache_resource
def load_engine():
    return PowercastPredictor()

engine = load_engine()

st.title("⚡ Auto-Powercast: Energy Infrastructure Intelligence Platform")
st.caption("Multi-Task Machine Learning for CapEx Estimation, Timeline Forecasting & Risk Assessment")

# Sidebar Controls
st.sidebar.header("🏗️ Project Parameters")
p_type = st.sidebar.selectbox("Energy Technology", ["Solar PV", "Wind Onshore", "Hydroelectric", "Thermal", "Nuclear"])
capacity = st.sidebar.slider("Installed Capacity (MW)", min_value=10.0, max_value=2000.0, value=250.0, step=10.0)
region = st.sidebar.selectbox("Deployment Region", ["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East & Africa"])
contractor = st.sidebar.selectbox("Contractor Tier", ["Tier-1 (Global EPC)", "Tier-2 (Regional)", "Tier-3 (Local)"])

input_data = {
    "capacity_mw": capacity,
    "project_type": p_type,
    "region": region,
    "contractor_tier": contractor
}

prediction = engine.predict(input_data)

# KPI Cards
col1, col2, col3 = st.columns(3)
col1.metric("Estimated CapEx Budget", f"${prediction['estimated_cost_usd_millions']:.2f} M", delta=f"{capacity} MW Scale")
col2.metric("Projected Timeline", f"{prediction['estimated_duration_months']:.1f} Months", delta="EPC Delivery")
risk_color = "red" if prediction['risk_assessment']['level'] == "High" else ("orange" if prediction['risk_assessment']['level'] == "Medium" else "green")
col3.metric("Project Risk Tier", prediction['risk_assessment']['level'], delta=f"Score: {prediction['risk_assessment']['score'] * 100:.0f}%")

st.divider()

# Tabbed Analytics
tab1, tab2 = st.tabs(["📊 Sensitivity & Cost Breakdown", "🔮 What-If Scenario Matrix"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("CapEx Allocation Forecast")
        cost = prediction['estimated_cost_usd_millions']
        breakdown_df = pd.DataFrame({
            "Category": ["Equipment & Turbines", "Civil & Structural", "Grid Interconnection", "Permitting & Labor", "Contingency Reserve"],
            "Cost_M": [cost * 0.42, cost * 0.23, cost * 0.15, cost * 0.12, cost * 0.08]
        })
        fig_pie = px.pie(breakdown_df, names="Category", values="Cost_M", hole=0.45, color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.subheader("Risk Exposure Gauge")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=prediction['risk_assessment']['score'] * 100,
            title={'text': f"Risk Index ({prediction['risk_assessment']['primary_risk_driver']})"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': risk_color},
                'steps': [
                    {'range': [0, 35], 'color': "#d4edda"},
                    {'range': [35, 70], 'color': "#fff3cd"},
                    {'range': [70, 100], 'color': "#f8d7da"}
                ]
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)

with tab2:
    st.subheader("Multi-Capacity Scaling Matrix")
    scale_mw = [50, 100, 250, 500, 750, 1000, 1500]
    sim_results = [engine.predict({"capacity_mw": mw, "project_type": p_type, "region": region, "contractor_tier": contractor}) for mw in scale_mw]
    
    sim_df = pd.DataFrame({
        "Capacity (MW)": scale_mw,
        "Estimated Cost ($M)": [r["estimated_cost_usd_millions"] for r in sim_results],
        "Duration (Months)": [r["estimated_duration_months"] for r in sim_results]
    })
    
    fig_line = px.line(sim_df, x="Capacity (MW)", y="Estimated Cost ($M)", markers=True, title=f"CapEx Scaling Curve for {p_type}")
    st.plotly_chart(fig_line, use_container_width=True)
    st.dataframe(sim_df, use_container_width=True)
