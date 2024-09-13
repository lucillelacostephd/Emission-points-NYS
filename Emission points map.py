# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 11:54:37 2024
An all pollutants and all emission points map. 
@author: lb945465
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap

df = pd.read_excel(r"C:\Users\LB945465\Desktop\Emissions inventory.xlsx")
df.columns
# Convert 'Year' column to integer data type
df['Year'] = df['Year'].fillna(0).astype(int)

# List of pollutants
pollutants = ['VOC (tons)', 'NOx (tons)', 'CO (tons)', 'CO2 (tons)', 'Particulates (tons)', 'PM10 (tons)', 'PM2.5 (tons)', 'HAPS (tons)', 'SO2 (tons)']

# Replace this part with a loop to get the coordinates of all the sites
sites = ['Bronx (133)', 'Bronx (83)', 'Queens', 'Kings', 'Richmond', 'Chester', 'Elizabeth']

site_rows = {}
site_coords = {}

for site in sites:
    site_rows[site] = df[df['Facility Name'] == site].dropna(subset=['Latitude', 'Longitude'])
    site_coords[site] = site_rows[site].iloc[0][['Latitude', 'Longitude']].to_dict()

# Drop rows with NaN values in the 'Latitude' and 'Longitude' columns
df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

# Drop the duplicate rows based on the 'Facility Name' and 'Year' columns, keeping the last occurrence
df.drop_duplicates(subset=['Facility Name', 'Year'], keep='last', inplace=True)

# Check again to confirm that the duplicates have been removed
duplicate_rows = df.duplicated(subset=['Facility Name', 'Year'], keep=False)

# Print the number of duplicate rows remaining (should be 0)
print(f'There are {duplicate_rows.sum()} duplicate rows based on the "Facility Name" and "Year" columns after removing duplicates.')

# Optionally, display the duplicate rows (should not display any rows)
if duplicate_rows.sum() > 0:
    print("Displaying duplicate rows:")
    print(df.loc[duplicate_rows, ['Facility Name', 'Year']])

# Filter by year
filter_by_year = False
start_year = 2021
end_year = 2021

if filter_by_year:
    df = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]

# Replace the data DataFrame with the top_emitters DataFrame
# Change to data=df if you want all emitters
data = df

# Recreate the map with the filtered data
m = folium.Map(location=[data['Latitude'].mean(), data['Longitude'].mean()], zoom_start=8)

# Add a marker for each sampling site
for site, row in site_rows.items():
    folium.Marker(
        location=[row.iloc[0]['Latitude'], row.iloc[0]['Longitude']],
        popup=site,
        icon=folium.Icon(color="red", icon="star"),
    ).add_to(m)

# Add bubbles to the map
for idx, row in data.iterrows():
    # Create a popup message with emission data for all pollutants
    popup_message = f'<strong>Facility:</strong> {row["Facility Name"]}<br><strong>Year:</strong> {row["Year"]}<br>'
    for pollutant in pollutants:
        if pd.notna(row[pollutant]):
            popup_message += f'<strong>{pollutant}:</strong> {row[pollutant]}<br>'
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=10,  # Fixed radius for simplicity
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.1,
        popup=popup_message,
    ).add_to(m)

# Add a heatmap to the map for each pollutant, excluding the NaN values
for pollutant in pollutants:
    heat_data = [[row['Latitude'], row['Longitude'], row[pollutant]] for idx, row in data.iterrows() if not pd.isnull(row[pollutant])]
    if heat_data:  # Check if heat_data is not empty
        HeatMap(heat_data).add_to(m)

# Create a new Marker Cluster with the filtered data
marker_cluster = MarkerCluster().add_to(m)

# Add bubbles to the map inside the marker cluster with the filtered data
for idx, row in data.iterrows():
    # Create a popup message with emission data for all pollutants
    popup_message = f'<strong>Facility:</strong> {row["Facility Name"]}<br><strong>Year:</strong> {row["Year"]}<br>'
    for pollutant in pollutants:
        if pd.notna(row[pollutant]):
            popup_message += f'<strong>{pollutant}:</strong> {row[pollutant]}<br>'
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=10,  # Fixed radius for simplicity
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.1,
        popup=popup_message,
    ).add_to(marker_cluster)

# Save the map to an HTML file
m.save(r'C:\Users\LB945465\Desktop\all_pollutants_map.html')
