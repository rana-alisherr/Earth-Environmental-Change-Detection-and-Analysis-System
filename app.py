

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
    "Analyze environmental changes across geographical "
    "regions using historical scientific data."
)

st.sidebar.header("Data Selection")

data_source = st.sidebar.radio(
    "Choose Data Source",
    ["Demonstration Data", "Upload CSV Data"]
)

# DEMONSTRATION DATA
if data_source == "Demonstration Data":

    rng = np.random.default_rng(42)
    years = np.arange(2000, 2026)

    variables = {
        "Temperature": (20, [0.08, -0.04, 0.02]),
        "Rainfall": (800, [5, -3, 1]),
        "Sea Level": (100, [3.5, 1.5, -0.5])
    }

    records = []

    for variable, (base, slopes) in variables.items():
        for i, region in enumerate(
            ["Region A", "Region B", "Region C"]
        ):
            for year in years:
                value = (
                    base
                    + slopes[i] * (year - 2000)
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
        "Demonstration mode: Data is simulated, "
        "not actual satellite observations."
    )

# UPLOAD REAL DATA
else:

    uploaded_file = st.file_uploader(
        "Upload environmental CSV file",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info("Upload a CSV file to begin analysis.")

        st.write("Required columns:")
        st.code("Year, Region, Variable, Value")

        st.stop()

    try:
        df = pd.read_csv(uploaded_file)
    except Exception as error:
        st.error(f"Could not read CSV: {error}")
        st.stop()

    required_columns = [
        "Year", "Region", "Variable", "Value"
    ]

    if not all(col in df.columns for col in required_columns):
        st.error(
            "Your CSV must contain these columns: "
            "Year, Region, Variable, Value"
        )
        st.stop()

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    df = df.dropna(subset=required_columns)

    if df.empty:
        st.error("No valid data found in the CSV.")
        st.stop()

    st.success("Environmental dataset uploaded successfully!")

# DATA PREVIEW
st.header("📊 Environmental Data")

st.dataframe(df.head(20), use_container_width=True)

st.caption(f"Total records: {len(df)}")

# FILTERS
st.sidebar.header("Analysis Filters")

selected_variable = st.sidebar.selectbox(
    "Environmental Variable",
    sorted(df["Variable"].astype(str).unique())
)

selected_region = st.sidebar.selectbox(
    "Geographical Region",
    sorted(df["Region"].astype(str).unique())
)

data = df[
    (df["Variable"].astype(str) == selected_variable)
    & (df["Region"].astype(str) == selected_region)
].copy()

data = data.sort_values("Year")

if len(data) < 3:
    st.warning(
        "At least 3 valid measurements are required "
        "for trend analysis."
    )
    st.stop()

if data["Year"].nunique() < 3:
    st.warning(
        "At least 3 different years are required."
    )
    st.stop()

# TREND ANALYSIS
result = linregress(data["Year"], data["Value"])

slope = result.slope
p_value = result.pvalue
r_squared = result.rvalue ** 2

if slope > 0:
    trend = "Increasing"
elif slope < 0:
    trend = "Decreasing"
else:
    trend = "Stable"

significant = p_value < 0.05

# RESULTS
st.header("🔍 Environmental Analysis")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Rate of Change",
    f"{slope:.4f} per year"
)

col2.metric(
    "Trend Direction",
    trend
)

col3.metric(
    "P-value",
    f"{p_value:.4f}"
)

st.metric("R-squared", f"{r_squared:.4f}")

# GRAPH
st.header("📈 Historical Change Visualization")

fig = px.scatter(
    data,
    x="Year",
    y="Value",
    title=f"{selected_variable} - {selected_region}",
    trendline="ols"
)

st.plotly_chart(fig, use_container_width=True)

# STATISTICAL SIGNIFICANCE
st.header("📐 Statistical Significance")

st.write(
    "Significance level: 0.05"
)

if significant:
    st.success(
        "The observed linear trend is statistically significant."
    )
else:
    st.warning(
        "The observed linear trend is not statistically significant."
    )

st.caption(
    "Statistical significance does not prove causation. "
    "Results depend on data quality and model assumptions."
)

# DOWNLOAD
st.header("📥 Download Analysis")

st.download_button(
    "Download Selected Data",
    data.to_csv(index=False),
    file_name="earthtrend_analysis.csv",
    mime="text/csv"
)

st.success("EarthTrend AI analysis completed!")

