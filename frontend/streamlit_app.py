import streamlit as st
import pandas as pd
import joblib
import numpy as np
import os

st.set_page_config(page_title="Auto PowerCast", layout="wide")

@st.cache_resource
def load_models():
    base = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(base)

    def find_file(filename):
        for folder in [base, parent]:
            path = os.path.join(folder, filename)
            if os.path.exists(path):
                return path
        raise FileNotFoundError(f"{filename} not found in {base} or {parent}")

    cost_model     = joblib.load(find_file("cost_model.pkl"))
    duration_model = joblib.load(find_file("duration_model.pkl"))
    risk_model     = joblib.load(find_file("risk_model.pkl"))
    encoder        = joblib.load(find_file("encoder.pkl"))
    return cost_model, duration_model, risk_model, encoder

try:
    cost_model, duration_model, risk_model, encoder = load_models()
    models_loaded = True
except Exception as e:
    st.error(f"Model loading error: {e}")
    models_loaded = False

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
    project_type = st.selectbox("Project Type", ["Solar", "Wind", "Hydro", "Thermal", "Transmission"])
    state = st.selectbox("State", ["Andhra Pradesh", "Gujarat", "Haryana", "Karnataka", "Madhya Pradesh", "Maharashtra", "Punjab", "Rajasthan", "Tamil Nadu", "Uttar Pradesh"])
    region = st.selectbox("Region", ["North", "South", "West", "Central"])
    capacity_mw = st.number_input("Capacity (MW)", min_value=1, value=500)
    sanctioned_budget_cr = st.number_input("Budget (Crores)", min_value=1.0, value=1200.0)

with col2:
    planned_duration_months = st.number_input("Planned Duration (Months)", min_value=1, value=36)
    contractor_count = st.number_input("Contractor Count", min_value=1, value=4)
    land_acquisition_status = st.selectbox("Land Acquisition Status", ["Complete", "Partial", "Pending"])
    project_complexity = st.selectbox("Project Complexity", ["Low", "Medium", "High"])
    cost_overrun_pct = st.slider("Cost Overrun %", 0, 50, 12)
    delay_months = st.slider("Delay Months", 0, 24, 5)

st.markdown("---")

if st.button("Predict Project Risk", disabled=not models_loaded):

    categorical_cols = ["project_type", "state", "region", "land_acquisition_status", "project_complexity"]

    input_dict = {
        "project_type": [project_type], "state": [state], "region": [region],
        "capacity_mw": [capacity_mw], "sanctioned_budget_cr": [sanctioned_budget_cr],
        "planned_duration_months": [planned_duration_months], "contractor_count": [contractor_count],
        "land_acquisition_status": [land_acquisition_status], "project_complexity": [project_complexity],
        "cost_overrun_pct": [cost_overrun_pct], "delay_months": [float(delay_months)]
    }

    input_df = pd.DataFrame(input_dict)

    try:
        encoded = encoder.transform(input_df[categorical_cols])
        encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(categorical_cols))
        numeric_df = input_df.drop(columns=categorical_cols).reset_index(drop=True)
        final_df = pd.concat([numeric_df, encoded_df.reset_index(drop=True)], axis=1)

        predicted_cost     = float(cost_model.predict(final_df)[0])
        predicted_duration = float(duration_model.predict(final_df)[0])
        predicted_risk     = str(risk_model.predict(final_df)[0])

        result = {
            "predicted_cost_cr": round(predicted_cost, 2),
            "predicted_duration_months": round(predicted_duration, 2),
            "predicted_risk_level": predicted_risk
        }

        st.session_state.result = result
        st.session_state.payload = input_dict
        st.session_state.history.append({
            "Project Type": project_type,
            "Predicted Cost (Cr)": round(predicted_cost, 2),
            "Predicted Duration (Months)": round(predicted_duration, 1),
            "Risk Level": predicted_risk
        })

    except Exception as e:
        st.error(f"Prediction error: {e}")

if st.session_state.result is not None:

    result  = st.session_state.result
    payload = st.session_state.payload

    st.markdown("---")
    st.success("Project Risk Assessment Complete")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Predicted Cost (Cr)", f"₹ {result['predicted_cost_cr']}")
    with c2:
        st.metric("Predicted Duration", f"{result['predicted_duration_months']} Months")
    with c3:
        st.metric("Risk Level", result["predicted_risk_level"])

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
    st.info(f"""
    Estimated Final Cost:      ₹{result['predicted_cost_cr']} Cr
    Estimated Completion Time: {result['predicted_duration_months']} Months
    Predicted Risk Category:   {result['predicted_risk_level']}
    """)

    st.markdown("---")
    st.subheader("Risk Score")
    st.metric("Risk Score", f"{risk_score}/100")

    if risk == "High":
        st.error("High Risk — Re-evaluate budget, review contractors, accelerate land acquisition, increase contingency reserves.")
    elif risk == "Medium":
        st.warning("Medium Risk — Monitor milestones closely, track budget deviations monthly, strengthen contractor coordination.")
    else:
        st.success("Low Risk — Proceed with execution, maintain regular monitoring, focus on operational efficiency.")

    st.markdown("---")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.caption("Predicted Cost (Cr)")
        st.bar_chart(pd.DataFrame({"Cost (Cr)": [result["predicted_cost_cr"]]}))
    with chart_col2:
        st.caption("Predicted Duration (Months)")
        st.bar_chart(pd.DataFrame({"Duration (Months)": [result["predicted_duration_months"]]}))

    st.markdown("---")
    st.subheader("Prediction History")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)

    st.markdown("---")
    report = f"""AUTO POWERCAST — PROJECT REPORT
===============================
Project Type:              {project_type}
State:                     {payload['state'][0]}
Region:                    {payload['region'][0]}
Capacity (MW):             {payload['capacity_mw'][0]}
Budget (Cr):               {payload['sanctioned_budget_cr'][0]}
Planned Duration (Months): {payload['planned_duration_months'][0]}
Contractor Count:          {payload['contractor_count'][0]}
Land Acquisition Status:   {payload['land_acquisition_status'][0]}
Project Complexity:        {payload['project_complexity'][0]}

---------------------------------
PREDICTIONS
---------------------------------
Predicted Cost:     ₹{result['predicted_cost_cr']} Cr
Predicted Duration: {result['predicted_duration_months']} Months
Predicted Risk:     {result['predicted_risk_level']}
Risk Score:         {risk_score}/100

---------------------------------
Generated by Auto PowerCast AI
Ministry of Power — ATH Hackathon 0.1 2026
"""
    st.download_button(label="Download Project Report", data=report, file_name="autopowercast_report.txt", mime="text/plain")