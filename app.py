
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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

    df["Region"] = df["Region"].astype(str)
    df["Variable"] = df["Variable"].astype(str)

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

variable_data = df[
    df["Variable"].astype(str) == selected_variable
].copy()

available_regions = sorted(
    variable_data["Region"].astype(str).unique()
)

if not available_regions:
    st.error("No regions are available for this variable.")
    st.stop()

selected_region = st.sidebar.selectbox(
    "Geographical Region (individual analysis)",
    available_regions
)

data = variable_data[
    variable_data["Region"].astype(str) == selected_region
].copy()

data = data.sort_values("Year")

if len(data) < 3 or data["Year"].nunique() < 3:
    st.warning(
        "At least 3 valid measurements from 3 different years "
        "are required for individual trend analysis."
    )
    st.stop()

# INDIVIDUAL TREND ANALYSIS
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
st.header("🔍 Individual Environmental Analysis")

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

# INDIVIDUAL GRAPH
st.header("📈 Historical Change Visualization")

fig = px.scatter(
    data,
    x="Year",
    y="Value",
    title=f"{selected_variable} - {selected_region}",
    trendline="ols"
)

st.plotly_chart(fig, use_container_width=True)

# MULTI-REGION COMPARISON
st.header("🌍 Multi-Region Comparison")

st.write(
    "Compare the same environmental variable across multiple "
    "geographical regions."
)

comparison_regions = st.multiselect(
    "Select regions to compare",
    options=available_regions,
    default=available_regions[:min(3, len(available_regions))]
)

if len(comparison_regions) < 2:

    st.info("Select at least two regions to display a comparison.")

else:

    comparison_data = variable_data[
        variable_data["Region"].isin(comparison_regions)
    ].copy()

    comparison_data = comparison_data.sort_values("Year")

    comparison_fig = go.Figure()

    comparison_results = []

    for region in comparison_regions:

        region_data = comparison_data[
            comparison_data["Region"] == region
        ].sort_values("Year")

        comparison_fig.add_trace(
            go.Scatter(
                x=region_data["Year"],
                y=region_data["Value"],
                mode="markers",
                name=f"{region} observations"
            )
        )

        if len(region_data) >= 3 and region_data["Year"].nunique() >= 3:

            region_result = linregress(
                region_data["Year"],
                region_data["Value"]
            )

            line_x = np.linspace(
                region_data["Year"].min(),
                region_data["Year"].max(),
                100
            )

            line_y = (
                region_result.intercept
                + region_result.slope * line_x
            )

            comparison_fig.add_trace(
                go.Scatter(
                    x=line_x,
                    y=line_y,
                    mode="lines",
                    name=f"{region} trend"
                )
            )

            if region_result.slope > 0:
                region_trend = "Increasing"
            elif region_result.slope < 0:
                region_trend = "Decreasing"
            else:
                region_trend = "Stable"

            comparison_results.append({
                "Region": region,
                "Rate of Change (per year)": round(
                    region_result.slope, 4
                ),
                "Trend Direction": region_trend,
                "R-squared": round(
                    region_result.rvalue ** 2, 4
                ),
                "P-value": round(
                    region_result.pvalue, 4
                ),
                "Statistically Significant": (
                    "Yes"
                    if region_result.pvalue < 0.05
                    else "No"
                )
            })

        else:

            comparison_results.append({
                "Region": region,
                "Rate of Change (per year)": "Insufficient data",
                "Trend Direction": "Insufficient data",
                "R-squared": "—",
                "P-value": "—",
                "Statistically Significant": "—"
            })

    comparison_fig.update_layout(
        title=f"{selected_variable}: Regional Comparison",
        xaxis_title="Year",
        yaxis_title=selected_variable,
        legend_title="Region and trend",
        hovermode="x unified"
    )

    st.plotly_chart(
        comparison_fig,
        use_container_width=True
    )

    st.subheader("📋 Regional Trend Comparison")

    comparison_table = pd.DataFrame(comparison_results)

    st.dataframe(
        comparison_table,
        use_container_width=True
    )

    st.download_button(
        "Download Regional Comparison",
        comparison_table.to_csv(index=False),
        file_name="earthtrend_region_comparison.csv",
        mime="text/csv"
    )

# STATISTICAL SIGNIFICANCE
st.header("📐 Statistical Significance")

st.write("Significance level: 0.05")

if significant:

    st.success(
        "The observed individual linear trend is statistically significant."
    )

else:

    st.warning(
        "The observed individual linear trend is not statistically significant."
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

