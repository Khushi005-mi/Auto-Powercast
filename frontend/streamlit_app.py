import streamlit as st
import requests
import pandas as pd
st.set_page_config(
    page_title="Auto PowerCast",
    layout="wide"
)
if "history" not in st.session_state:
    st.session_state.history = []

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
        0,
        50,
        12
    )

    delay_months = st.slider(
        "Delay Months",
        0,
        24,
        5
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

        # Save prediction history
        st.session_state.history.append({
            "Project Type": project_type,
            "Predicted Cost": round(result["predicted_cost_cr"], 2),
            "Predicted Duration": round(result["predicted_duration_months"], 1),
            "Risk": result["predicted_risk_level"]
        })

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
            st.error(
                "⚠ High Risk Project"
            )

        elif risk == "Medium":
            st.warning(
                "⚠ Medium Risk Project"
            )

        else:
            st.success(
                "✓ Low Risk Project"
            )

        st.markdown("---")

        st.subheader("Executive Summary")

        st.info(
            f"""
            Estimated Final Cost: ₹{round(result['predicted_cost_cr'],2)} Cr

            Estimated Completion Time: {round(result['predicted_duration_months'],1)} Months

            Predicted Risk Category: {result['predicted_risk_level']}
            """
        )

        st.markdown("---")

        st.subheader("Prediction History")

        history_df = pd.DataFrame(
            st.session_state.history
        )

        st.dataframe(
            history_df,
            use_container_width=True
        )

        st.markdown("---")

        st.subheader("Predicted Cost")

        st.bar_chart(
            pd.DataFrame({
                "Cost (Cr)": [result["predicted_cost_cr"]]
            })
        )

        st.subheader("Predicted Duration")

        st.bar_chart(
            pd.DataFrame({
                "Duration (Months)": [result["predicted_duration_months"]]
            })
        )
        st.markdown("---")

        st.subheader("AI Recommendations")

        risk = result["predicted_risk_level"]
        if risk == "High":
          risk_score = 85

        elif risk == "Medium":
          risk_score = 60

        else:
          risk_score = 25

        st.metric(
            "Risk Score",
            f"{risk_score}/100"
)

        if risk == "High":

            st.error(
                """
                High Risk Project

                Recommendations:
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
                Medium Risk Project

                Recommendations:
                • Monitor milestones closely
                • Track budget deviations monthly
                • Strengthen contractor coordination
                • Review schedule risks regularly
                """
            )

        else:

            st.success(
                """
                Low Risk Project

                Recommendations:
                • Proceed with execution
                • Maintain regular monitoring
                • Continue current planning strategy
                • Focus on operational efficiency
                """
            )

    except Exception as e:
                st.markdown("---")

    report = f"""
        POWERCAST AI PROJECT REPORT
        ===========================

        Project Type: {project_type}
        State: {state}
        Region: {region}

        Capacity (MW): {capacity_mw}
        Budget (Cr): {sanctioned_budget_cr}

        Planned Duration: {planned_duration_months}
        Contractor Count: {contractor_count}

        Land Acquisition Status: {land_acquisition_status}
        Project Complexity: {project_complexity}

        ---------------------------------

        PREDICTIONS

        Predicted Cost: {round(result['predicted_cost_cr'], 2)} Cr

        Predicted Duration:
        {round(result['predicted_duration_months'], 1)} Months

        Predicted Risk:
        {result['predicted_risk_level']}

        ---------------------------------

        Generated by PowerCast AI
        """

    st.download_button(
            label="Download Project Report",
            data=report,
            file_name="powercast_report.txt",
            mime="text/plain"
        )

try:

    response = requests.post(
        "http://127.0.0.1:8000/predict",
        json=payload
    )

    response.raise_for_status()

    result = response.json()

except Exception as e:

    st.error(
        f"API Error: {e}"
    )