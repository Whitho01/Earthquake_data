import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Global Earthquake Map", layout="wide")

st.title("Global Earthquake Map")
st.markdown("Interactively explore global earthquake data by year and metric.")

# --- Load data ---
df = pd.read_csv('earthquake_data.csv')
df['time'] = pd.to_datetime(df['date_time'], dayfirst=True)
df['year'] = df['time'].dt.year

df_melted = df.melt(
    id_vars=['latitude', 'longitude', 'time', 'year', 'location'],
    value_vars=['magnitude', 'mmi', 'cdi', 'sig'],
    var_name='metric',
    value_name='intensity'
)


year = st.slider(
    "Select Year",
    min_value=int(df['year'].min()),
    max_value=int(df['year'].max()),
    value=int(df['year'].min()),
    step=1
)

metric = st.selectbox(
    "Select Intensity Metric",
    options=['magnitude', 'mmi', 'cdi', 'sig'],
    index=0
)
metric_values = df_melted[df_melted['metric'] == metric]['intensity']
intensity_min = float(metric_values.min())
intensity_max = float(metric_values.max())

intensity_range = st.slider(
    "Select Intensity Range",
    min_value=intensity_min,
    max_value=intensity_max,
    value=(intensity_min, intensity_max)
)

top_n = st.slider("Show Top N Earthquakes", 5, 50, 10)

filtered = df_melted[
    (df_melted['year'] == year) &
    (df_melted['metric'] == metric) &
    (df_melted['intensity'] >= intensity_range[0]) &
    (df_melted['intensity'] <= intensity_range[1])
]
filtered = filtered.dropna(subset=['latitude', 'longitude', 'intensity'])

st.markdown("### Summary Statistics")
st.metric("Total Earthquakes", len(filtered))
st.metric("Max Intensity", filtered['intensity'].max() if not filtered.empty else "N/A")
st.metric("Average Intensity", round(filtered['intensity'].mean(), 2) if not filtered.empty else "N/A")

world_map = alt.topo_feature('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json', 'countries')
base = alt.Chart(world_map).mark_geoshape(
    fill='lightgray',
    stroke='white'
).project('equirectangular').properties(
    width=900,
    height=500
)

points = alt.Chart(filtered).mark_circle(opacity=0.7).encode(
    longitude='longitude:Q',
    latitude='latitude:Q',
    size=alt.Size('intensity:Q', scale=alt.Scale(type='sqrt', range=[20, 300]), legend=None),
    color=alt.Color('intensity:Q', scale=alt.Scale(scheme='plasma')),
    tooltip=['location:N', 'time:T', 'intensity:Q']
)

chart = base + points

st.altair_chart(chart, use_container_width=True)
if not filtered.empty:
    top_earthquakes = filtered.sort_values('intensity', ascending=False).head(top_n)
    st.markdown(f"### Top {top_n} Strongest Earthquakes")
    st.dataframe(top_earthquakes[['time', 'location', 'intensity', 'latitude', 'longitude']])
else:
    st.write("No earthquakes match the filters.")
