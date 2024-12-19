# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 17:40:25 2024

@author: lb945465
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
from branca.element import Template, MacroElement

# Load the data
df = pd.read_excel(r"C:\Users\LB945465\Desktop\Emissions inventory.xlsx")
df['Year'] = df['Year'].fillna(0).astype(int)

# Set pollutant and year range
Pollutant = 'VOC (tons)'
start_year, end_year = 2000, 2021

# Filter data by year and drop missing coordinates
df = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)].dropna(subset=['Latitude', 'Longitude'])

# Get top 250 emitters
top_emitters = df.nlargest(1000, Pollutant)
data = top_emitters.copy()

# Deduplicate data by Facility Name and coordinates
deduplicated_data = data.groupby(['Facility Name', 'Latitude', 'Longitude']).apply(
    lambda group: pd.DataFrame({
        'Year': group['Year'],
        Pollutant: group[Pollutant]
    }).sort_values('Year').to_dict(orient='records')
).reset_index(name='yearly_data')

# Create the base map
m = folium.Map(location=[data['Latitude'].mean(), data['Longitude'].mean()], zoom_start=8)

# Add heatmap
heat_data = [[row['Latitude'], row['Longitude'], sum(d[Pollutant] for d in row['yearly_data'])] for _, row in deduplicated_data.iterrows()]
HeatMap(heat_data).add_to(m)

# Create a MarkerCluster
marker_cluster = MarkerCluster().add_to(m)

# Add markers to the cluster
for _, row in deduplicated_data.iterrows():
    yearly_emissions = "<br>".join(
        f"<strong>{entry['Year']}:</strong> {entry[Pollutant]} tons" for entry in row['yearly_data']
    )
    popup_content = f"""
        <strong>Facility:</strong> {row['Facility Name']}<br>
        <strong>Yearly VOC Emissions:</strong><br>{yearly_emissions}
    """
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_content, max_width=300),
    ).add_to(marker_cluster)

# List of sampling sites with their names and coordinates
sampling_sites = {
    'Bronx': {'Latitude': 40.8679, 'Longitude': -73.87809},
    'Queens': {'Latitude': 40.73614, 'Longitude': -73.82153},
    'Kings': {'Latitude': 40.69454, 'Longitude': -73.92769},
    'Richmond': {'Latitude': 40.58027, 'Longitude': -74.19832},
    'Chester': {'Latitude': 40.787628, 'Longitude': -74.676301},
    'Elizabeth': {'Latitude': 40.64144, 'Longitude': -74.208365},
}

# Add sampling site markers to the map
for site, coords in sampling_sites.items():
    folium.Marker(
        location=[coords['Latitude'], coords['Longitude']],
        popup=f"<strong>Sampling Site:</strong> {site}",
        icon=folium.Icon(color="red", icon="star"),
    ).add_to(m)

# Add legend
legend_html = """
<div style="
    position: fixed;
    bottom: 50px; left: 50px; width: 250px; height: 120px;
    background-color: white; z-index:1000; font-size:14px;
    border:2px solid grey; padding: 10px;">
    <b>Legend</b><br>
    <i style="background:blue; width: 10px; height: 10px; display: inline-block;"></i> Emission Points<br>
    <i style="background:red; width: 10px; height: 10px; display: inline-block;"></i> Sampling Sites<br>
    <i style="background:rgba(0, 0, 255, 0.6); width: 10px; height: 10px; display: inline-block;"></i> Heatmap Intensity<br>
</div>
"""
legend = MacroElement()
legend._template = Template(legend_html)
m.get_root().add_child(legend)

# Save the map to an HTML file
m.save(r'C:\Users\LB945465\Desktop\final_bubble_map_with_sites.html')
