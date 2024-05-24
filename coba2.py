import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

@st.cache_data
def load_data():
     url = "https://raw.githubusercontent.com/Lexie88rus/bank-marketing-analysis/master/bank.csv"
     return pd.read_csv(url)

df = load_data()

st.set_page_config(
     page_title="Modern Dashboard",
     page_icon="📊",
     layout="wide",
     initial_sidebar_state="expanded",
 )

st.sidebar.header("Filter Options")

job_filter = st.sidebar.multiselect(
     "Select Job Type:",
     options=df["job"].unique(),
     default=df["job"].unique()
 )

age_filter = st.sidebar.slider(
     "Select Age Range:",
     min_value=int(df["age"].min()),
     max_value=int(df["age"].max()),
     value=(int(df["age"].min()), int(df["age"].max()))
 )

df_filtered = df[
     (df["job"].isin(job_filter)) &
     (df["age"] >= age_filter[0]) &
     (df["age"] <= age_filter[1])
 ]

st.title("Modern Interactive Dashboard")

 # Displaying Key Metrics
total_customers = len(df_filtered)

avg_balance = round(df_filtered['balance'].mean(), 2)

col1, col2 = st.columns(2)

with col1:
     st.metric(label="Total Customers", value=total_customers)

with col2:
     st.metric(label="Average Balance", value=f"${avg_balance}")

  # Plotting Charts
fig_age_dist = px.histogram(
                df_filtered, x='age', nbins=30, title='Age Distribution')
fig_job_dist = px.pie(df_filtered, names='job', title='Job Distribution')

  # Displaying Charts in Columns
col3, col4 = st.columns(2)
  
with col3:
      st.plotly_chart(fig_age_dist)
      
with col4:
      st.plotly_chart(fig_job_dist)

  # Additional Analysis Section
if st.checkbox("Show Raw Data"):
      st.subheader("Raw Data")
      st.write(df_filtered)