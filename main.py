import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
# import pandas as pd

"""
# Customer Data Analysis

This data is from Apollo.io. This is analysis of employees that have the keyword "ADAS" in their titles.
"""

## heat map
df = pd.read_csv('./data/long_lat_combined.csv')
df = df.dropna(subset=['Latitude'])
m = folium.Map(location=[30, -90], zoom_start=4)

heat_data = [[row['Latitude'], row['Longitude']] for index, row in df.iterrows()]
HeatMap(heat_data, radius=15).add_to(m)

## streamlit display
with st.container():
   st.write("Create a bounding box to zoom.")
   st.plotly_chart(fig)

with st.container():
    st.write("These are the locations of ADAS employees/companies.")
    st_data = st_folium(m, width=725)