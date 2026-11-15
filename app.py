
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import linregress

st.set_page_config(
    page_title="EarthTrend AI",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 EarthTrend AI")
st.subheader("Earth Environmental Change Detection & Analysis")

st.write(
    "Explore environmental changes across regions "
    "and analyze their trends over time."
)

# Generate clearly labelled demonstration data
rng = np.random.default_rng(42)

years = np.arange(2000, 2026)

regions = ["Region A", "Region B", "Region C"]

variables = {
    "Temperature": {
        "unit": "°C",
        "base": 20,
        "slopes": [0.08, -0.04, 0.02]
    },
    "Rainfall": {
        "unit": "mm",
        "base": 800,
        "slopes": [5, -3, 1]
    },
    "Sea Level": {
        "unit": "mm",
        "base": 100,
        "slopes": [3.5, 1.5, -0.5]
    }
}

records = []

for variable, info in variables.items():
    for i, region in enumerate(regions):
        for year in years:
            value = (
                info["base"]
                + info["slopes"][i] * (year - 2000)
                + rng.normal(0, 2)
            )

            records.append({
                "Year": year,
                "Region": region,
                "Variable": variable,
                "Value": value
            })

df = pd.DataFrame(records)

st.info(
    "Demo mode: These are simulated data, "
    "not actual satellite observations."
)

# User selections
col1, col2 = st.columns(2)

with col1:
    selected_variable = st.selectbox(
        "Select Environmental Variable",
        list(variables.keys())
    )

with col2:
    selected_region = st.selectbox(
        "Select Geographical Region",
        regions
    )

# Filter data
data = df[
    (df["Variable"] == selected_variable) &
    (df["Region"] == selected_region)
].copy()

# Statistical analysis
result = linregress(data["Year"], data["Value"])

slope = result.slope
p_value = result.pvalue

trend = (
    "Increasing" if slope > 0
    else "Decreasing" if slope < 0
    else "Stable"
)

significant = p_value < 0.05

# Results
st.header("Environmental Analysis")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Rate of Change",
    f"{slope:.3f} {variables[selected_variable]['unit']}/year"
)

c2.metric("Trend Direction", trend)

c3.metric("P-value", f"{p_value:.4f}")

# Graph
st.header("Historical Change Visualization")

fig = px.line(
    data,
    x="Year",
    y="Value",
    markers=True,
    title=f"{selected_variable} - {selected_region}"
)

fig.update_layout(
    xaxis_title="Year",
    yaxis_title=variables[selected_variable]["unit"]
)

st.plotly_chart(fig, use_container_width=True)

# Statistical significance
st.header("Statistical Significance")

if significant:
    st.success(
        "The observed linear trend is statistically significant "
        "at the 0.05 level."
    )
else:
    st.warning(
        "The observed linear trend is not statistically significant "
        "at the 0.05 level."
    )

st.write(f"R-squared: {result.rvalue ** 2:.4f}")

st.caption(
    "Results are based on simulated demonstration data. "
    "Statistical significance does not establish causation."
)

# Download results
st.header("Download Analysis")

csv = data.to_csv(index=False)

st.download_button(
    "Download Selected Data (CSV)",
    csv,
    file_name="earthtrend_analysis.csv",
    mime="text/csv"
)
