import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Auto PowerCast",
    layout="wide"
)

if "history" not in st.session_state:
    st.session_state.history = []

if "result" not in st.session_state:
    st.session_state.result = None

if "payload" not in st.session_state:
    st.session_state.payload = None

st.title("Auto PowerCast")
st.subheader("AI-Powered Power Infrastructure Risk Forecasting")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    project_type = st.selectbox(
        "Project Type",
        ["Solar", "Wind", "Hydro", "Thermal", "Transmission"]
    )

    state = st.selectbox(
        "State",
        [
            "Andhra Pradesh",
            "Gujarat",
            "Haryana",
            "Karnataka",
            "Madhya Pradesh",
            "Maharashtra",
            "Punjab",
            "Rajasthan",
            "Tamil Nadu",
            "Uttar Pradesh"
        ]
    )

    region = st.selectbox(
        "Region",
        ["North", "South", "West", "Central"]
    )

    capacity_mw = st.number_input(
        "Capacity (MW)",
        min_value=1,
        value=500
    )

    sanctioned_budget_cr = st.number_input(
        "Budget (Crores)",
        min_value=1.0,
        value=1200.0
    )

with col2:
    planned_duration_months = st.number_input(
        "Planned Duration (Months)",
        min_value=1,
        value=36
    )

    contractor_count = st.number_input(
        "Contractor Count",
        min_value=1,
        value=4
    )

    land_acquisition_status = st.selectbox(
        "Land Acquisition Status",
        ["Complete", "Partial", "Pending"]
    )

    project_complexity = st.selectbox(
        "Project Complexity",
        ["Low", "Medium", "High"]
    )

    cost_overrun_pct = st.slider(
        "Cost Overrun %",
        0, 50, 12
    )

    delay_months = st.slider(
        "Delay Months",
        0, 24, 5
    )

st.markdown("---")

if st.button("Predict Project Risk"):

    payload = {
        "project_type": project_type,
        "state": state,
        "region": region,
        "capacity_mw": capacity_mw,
        "sanctioned_budget_cr": sanctioned_budget_cr,
        "planned_duration_months": planned_duration_months,
        "contractor_count": contractor_count,
        "land_acquisition_status": land_acquisition_status,
        "project_complexity": project_complexity,
        "cost_overrun_pct": cost_overrun_pct,
        "delay_months": delay_months
    }

    try:
        response = requests.post(
            "http://127.0.0.1:8000/predict",
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        st.session_state.result = result
        st.session_state.payload = payload

        st.session_state.history.append({
            "Project Type": project_type,
            "Predicted Cost (Cr)": round(result["predicted_cost_cr"], 2),
            "Predicted Duration (Months)": round(result["predicted_duration_months"], 1),
            "Risk Level": result["predicted_risk_level"]
        })

    except Exception as e:
        st.error(f"API Error: {e}. Make sure your FastAPI backend is running on port 8000.")
        st.session_state.result = None

# Show results only if prediction was successful
if st.session_state.result is not None:

    result = st.session_state.result
    payload = st.session_state.payload

    st.markdown("---")
    st.success("Project Risk Assessment Complete")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Predicted Cost (Cr)",
            f"₹ {round(result['predicted_cost_cr'], 2)}"
        )

    with c2:
        st.metric(
            "Predicted Duration",
            f"{round(result['predicted_duration_months'], 1)} Months"
        )

    with c3:
        st.metric(
            "Risk Level",
            result["predicted_risk_level"]
        )

    risk = result["predicted_risk_level"]

    if risk == "High":
        st.error("⚠ High Risk Project")
        risk_score = 85
    elif risk == "Medium":
        st.warning("⚠ Medium Risk Project")
        risk_score = 60
    else:
        st.success("✓ Low Risk Project")
        risk_score = 25

    st.markdown("---")
    st.subheader("Executive Summary")

    st.info(
        f"""
        Estimated Final Cost: ₹{round(result['predicted_cost_cr'], 2)} Cr

        Estimated Completion Time: {round(result['predicted_duration_months'], 1)} Months

        Predicted Risk Category: {result['predicted_risk_level']}
        """
    )

    st.markdown("---")
    st.subheader("Risk Score")
    st.metric("Risk Score", f"{risk_score}/100")

    if risk == "High":
        st.error(
            """
            High Risk Project — Recommendations:
            • Re-evaluate budget allocation
            • Review contractor performance
            • Accelerate land acquisition
            • Increase contingency reserves
            • Conduct detailed risk assessment
            """
        )
    elif risk == "Medium":
        st.warning(
            """
            Medium Risk Project — Recommendations:
            • Monitor milestones closely
            • Track budget deviations monthly
            • Strengthen contractor coordination
            • Review schedule risks regularly
            """
        )
    else:
        st.success(
            """
            Low Risk Project — Recommendations:
            • Proceed with execution
            • Maintain regular monitoring
            • Continue current planning strategy
            • Focus on operational efficiency
            """
        )

    st.markdown("---")
    st.subheader("Cost & Duration Charts")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.caption("Predicted Cost (Cr)")
        st.bar_chart(
            pd.DataFrame({
                "Cost (Cr)": [result["predicted_cost_cr"]]
            })
        )

    with chart_col2:
        st.caption("Predicted Duration (Months)")
        st.bar_chart(
            pd.DataFrame({
                "Duration (Months)": [result["predicted_duration_months"]]
            })
        )

    st.markdown("---")
    st.subheader("Prediction History")

    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df, use_container_width=True)

    st.markdown("---")

    report = f"""AUTO POWERCAST — PROJECT REPORT
===============================

Project Type:              {result.get('project_type', payload.get('project_type', 'N/A'))}
State:                     {payload.get('state', 'N/A')}
Region:                    {payload.get('region', 'N/A')}
Capacity (MW):             {payload.get('capacity_mw', 'N/A')}
Budget (Cr):               {payload.get('sanctioned_budget_cr', 'N/A')}
Planned Duration (Months): {payload.get('planned_duration_months', 'N/A')}
Contractor Count:          {payload.get('contractor_count', 'N/A')}
Land Acquisition Status:   {payload.get('land_acquisition_status', 'N/A')}
Project Complexity:        {payload.get('project_complexity', 'N/A')}

---------------------------------
PREDICTIONS
---------------------------------

Predicted Cost:     ₹{round(result['predicted_cost_cr'], 2)} Cr
Predicted Duration: {round(result['predicted_duration_months'], 1)} Months
Predicted Risk:     {result['predicted_risk_level']}
Risk Score:         {risk_score}/100

---------------------------------
Generated by Auto PowerCast AI
Ministry of Power — ATH Hackathon 0.1 2026
"""

    st.download_button(
        label="Download Project Report",
        data=report,
        file_name="autopowercast_report.txt",
        mime="text/plain"
    )