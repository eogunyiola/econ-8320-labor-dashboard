
import streamlit as st
import pandas as pd

st.title("US Labor Statistics Dashboard")

# Load the data
data = pd.read_csv("labor_statistics.csv")

# Display raw data
if st.checkbox("Show raw data"):
    st.write(data)

# Create a chart
chart = st.line_chart(data.pivot(index="date", columns="series", values="value"))



