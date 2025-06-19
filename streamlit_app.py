import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Global Earthquake Map", layout="wide")

st.title("Global Earthquake Map")

with st.expander("What do the intensity metrics mean?"):
    st.markdown("""
    **Magnitude:** A measure of the energy released at the source of the earthquake.

    **MMI (Modified Mercalli Intensity):** A subjective scale of shaking intensity based on observed effects.

    **CDI (Community Determined Intensity):** Intensity based on reports from people experiencing the earthquake.

    **SIG (Significance):** A calculated significance score considering magnitude, depth, and location.
    """)
    
df = pd.read_csv('earthquake_data.csv')
df['time'] = pd.to_datetime(df['date_time'], dayfirst=True)
df['year'] = df['time'].dt.year

df_melted = df.melt(
    id_vars=['latitude', 'longitude', 'time', 'year', 'location'],
    value_vars=['magnitude', 'mmi', 'cdi', 'sig'],
    var_name='metric',
    value_name='intensity'
)

with st.expander(" Filter Options", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        year = st.slider(
            "Select Year",
            min_value=int(df['year'].min()),
            max_value=int(df['year'].max()),
            value=int(df['year'].min()),
            step=1
        )
    with col2:
        metric = st.selectbox(
            "Select Intensity Metric",
            options=['magnitude', 'mmi', 'cdi', 'sig'],
            index=0
        )
metric_values = df_melted[df_melted['metric'] == metric]['intensity']
intensity_min = float(metric_values.min())
intensity_max = float(metric_values.max())

filtered = df_melted[
    (df_melted['year'] == year) &
    (df_melted['metric'] == metric) 
].dropna(subset=['latitude', 'longitude', 'intensity'])

st.markdown("### Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Year", year)
col2.metric("Metric", metric.capitalize())
col3.metric("Total Earthquakes", len(filtered))
col4.metric("Max Intensity", filtered['intensity'].max() if not filtered.empty else "N/A")

col5, col6 = st.columns(2)
col5.metric("Average Intensity", round(filtered['intensity'].mean(), 2) if not filtered.empty else "N/A")

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
    size=alt.value(60),
    color=alt.Color('intensity:Q', scale=alt.Scale(scheme='viridis'), legend = alt.Legend(title = "Intensity"),
    tooltip=['location:N', 'time:T', 'intensity:Q']
)

chart = base + points

top_n = 5
st.altair_chart(chart, use_container_width=True)
if not filtered.empty:
    top_earthquakes = filtered.sort_values('intensity', ascending=False).head(top_n)
    st.markdown(f"### Top {top_n} Strongest Earthquakes")
    st.dataframe(top_earthquakes[['time', 'location', 'intensity', 'latitude', 'longitude']])
else:
    st.write("No earthquakes match the filters.")
