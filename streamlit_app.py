import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Global Earthquake Map", layout="wide")

st.title("🌍 Global Earthquake Map")
st.markdown("Interactively explore global earthquake data by year and metric.")

# --- Load data ---
@st.cache_data
def load_data():
    df = pd.read_csv("earthquake_data.csv")
    df['time'] = pd.to_datetime(df['date_time'], dayfirst=True)
    df['year'] = df['time'].dt.year
    return df

df = load_data()

# --- Melt data for metric filtering ---
df_melted = df.melt(
    id_vars=['latitude', 'longitude', 'time', 'year', 'location'],
    value_vars=['magnitude', 'mmi', 'cdi', 'sig'],
    var_name='metric',
    value_name='intensity'
)

# --- Sidebar filters ---
st.sidebar.header("Filters")

year = st.sidebar.slider(
    "Select Year",
    min_value=int(df['year'].min()),
    max_value=int(df['year'].max()),
    value=int(df['year'].min()),
    step=1
)

metric = st.sidebar.selectbox(
    "Select Intensity Metric",
    options=['magnitude', 'mmi', 'cdi', 'sig'],
    index=0
)

# --- Filtered data ---
filtered = df_melted[(df_melted['year'] == year) & (df_melted['metric'] == metric)]

# --- Altair chart ---
chart = alt.Chart(filtered).mark_circle(opacity=0.7).encode(
    longitude='longitude:Q',
    latitude='latitude:Q',
    size=alt.Size('intensity:Q', scale=alt.Scale(type='sqrt', range=[20, 300]), legend=None),
    color=alt.Color('intensity:Q', scale=alt.Scale(scheme='plasma'), legend=alt.Legend(title='Intensity')),
    tooltip=['location:N', 'time:T', 'intensity:Q']
).properties(
    width=900,
    height=500,
    title=f"Earthquakes in {year} — Metric: {metric.upper()}"
).configure_title(
    fontSize=20,
    anchor='start'
)

# --- Display chart ---
st.altair_chart(chart, use_container_width=True)

st.markdown("Data source: *Your dataset description or source here.*")
