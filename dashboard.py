
import streamlit as st
import pandas as pd

# Load the data
data = pd.read_csv("labor_statistics.csv")

# Dashboard Title
st.title("US Labor Statistics Dashboard")

# Show raw data (optional)
if st.checkbox("Show raw data"):
    st.write(data)

# Select a series to plot
selected_series = st.selectbox("Select a series to visualize:", data["series"].unique())

# Filter data for the selected series
filtered_data = data[data["series"] == selected_series]

# Plot the data
st.line_chart(filtered_data.set_index("date")["value"])
