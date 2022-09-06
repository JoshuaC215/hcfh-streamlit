import pandas as pd
import streamlit as st
import datetime
import numpy as np
import altair as alt
import os
import s3fs

data_url = os.getenv("DATAPATH", default="./data/by-month-site.csv")
s3_filepath = os.getenv("S3_FILEPATH")
s3 = s3fs.S3FileSystem(anon=False)

st.header("Exploring High Country Food Hub Orders")

#@st.cache
def load_orders():
    data = pd.DataFrame([])
    if s3_filepath:
        data = pd.read_csv(s3.open(s3_filepath, mode="rb"), thousands=",")
    else:
        data = pd.read_csv(data_url, thousands=",")
    lowercase = lambda x: str(x).lower()
    to_month = lambda dt: datetime.date(dt.year, dt.month, 1)
    data.rename(lowercase, axis="columns", inplace=True)
    data["distribution month"] = pd.to_datetime(data["distribution month"])
    data["distribution month"] = data["distribution month"].map(to_month)
    return data

data_load_state = st.text("Loading data...")
orders = load_orders()
data_load_state.text("Done! (using st.cache)")

if st.checkbox("Show raw data"):
    st.subheader("Raw data")
    st.write(orders.head(30))

st.subheader("Orders by month")

by_month = orders.groupby(by=["distribution month"])["order total"].sum()
st.bar_chart(by_month)

st.subheader("Orders by satellite site over time")
by_month_site = orders.groupby(by=["location", "distribution month"])["order total"].sum()

sites = st.multiselect(
    "Choose satellite site", by_month_site.index.get_level_values(0).unique(), ["High Country Food Hub (Wed)"]
)
if not sites:
    st.error("Please select at least one site.")
else:
    data = by_month_site.loc[sites]
    data = data.T.reset_index()
    chart = (
        alt.Chart(data)
        .mark_area(opacity=0.7)
        .encode(
            x="distribution month:T",
            y=alt.Y("order total:Q", stack=True),
            color="location:N",
        )
    )
    st.altair_chart(chart, use_container_width=True)