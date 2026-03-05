import streamlit as st
import numpy as np
import pandas as pd

from tests.registry import REGISTRY, get_allowed_tests
from recommendations import recommend_test

st.set_page_config(page_title="Public Health Biostatistics Lab", layout="wide")

st.title("📊 Public Health Biostatistics Lab")
st.markdown("Decision-guided statistical analysis for epidemiology students.")

st.divider()

st.markdown("""
The app selects statistical tests based on:

• Study design  
• Outcome type  
• Exposure type  
""")

teaching_mode = st.toggle("Teaching Mode (Show Learning Guidance)", value=True)

st.divider()

st.header("Study Configuration")

design = st.selectbox(
    "Study Design",
    ["independent", "paired"]
)

y_type = st.selectbox(
    "Outcome Type",
    ["binary", "continuous", "time-to-event"]
)

x_type = st.selectbox(
    "Exposure Type",
    ["binary", "categorical", "continuous"]
)

groups_k = st.number_input(
    "Number of Groups (if categorical exposure)",
    min_value=2,
    value=2,
    disabled=(x_type != "categorical")
)

meta = {
    "design": design,
    "y_type": y_type,
    "x_type": x_type,
    "groups_k": groups_k
}

st.divider()

st.header("Statistical Decision Path")

recommended_test = recommend_test(meta)

decision_steps = []

decision_steps.append(f"Study design: {design}")
decision_steps.append(f"Outcome type: {y_type}")
decision_steps.append(f"Exposure type: {x_type}")

if x_type == "categorical":
    decision_steps.append(f"Number of groups: {groups_k}")

if recommended_test:
    decision_steps.append(f"Recommended Test: {recommended_test}")
else:
    decision_steps.append("No statistical test matched.")

for step in decision_steps:
    st.write("•", step)
