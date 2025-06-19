import streamlit as st
import pandas as pd
import altair as alt
import pydeck as pdk

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

#Added changes here!

if not filtered.empty:
    st.markdown("### Earthquake Map (Zoomable)")

    # Set view to center on the mean of the filtered data
    midpoint = (filtered["latitude"].mean(), filtered["longitude"].mean())

    view_state = pdk.ViewState(
        latitude=midpoint[0],
        longitude=midpoint[1],
        zoom=2,  # You can change this default zoom level
        pitch=0,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered,
        get_position='[longitude, latitude]',
        get_color='[255, 140, 0, 160]',
        get_radius=50000,  # adjust radius or tie to intensity
        pickable=True,
        tooltip=True,
    )

    tooltip = {
        "html": "<b>Location:</b> {location}<br/>"
                "<b>Time:</b> {time}<br/>"
                "<b>Intensity:</b> {intensity}",
        "style": {"backgroundColor": "steelblue", "color": "white"},
    }

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light"
    )

    st.pydeck_chart(deck)
else:
    st.write("No earthquakes match the filters.")


