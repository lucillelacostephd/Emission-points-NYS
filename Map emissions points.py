# -*- coding: utf-8 -*-
"""
Created on Sun Sep 10 17:41:37 2023
(FIRST VERSION) Plot to create a figure showing the emission points.
@author: lb945465
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
from geopy.distance import great_circle

df= pd.read_excel(r"C:\Users\LB945465\OneDrive - University at Albany - SUNY\State University of New York\NYSERDA VOC project\Data\Title_V_Emissions_Inventory__2010-2021_data for case study.xlsx",
                  )
df.columns
# Convert 'Year' column to integer data type
df['Year'] = df['Year'].fillna(0).astype(int)

# Set pollutant here
Pollutant='SO2 (tons)' #'VOC (tons)', 'NOx (tons)', 'CO (tons)', 'CO2 (tons)', 'Particulates (tons)', 'PM10 (tons)', 'PM2.5 (tons)', 'HAPS (tons)', 'SO2 (tons)'

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
df.drop_duplicates(subset=['Facility Name', 'Year', Pollutant], keep='last', inplace=True)

# Check again to confirm that the duplicates have been removed
duplicate_rows = df.duplicated(subset=['Facility Name', 'Year', Pollutant], keep=False)

# Print the number of duplicate rows remaining (should be 0)
print(f'There are {duplicate_rows.sum()} duplicate rows based on the "Facility Name" and "Year" columns after removing duplicates.')

# Optionally, display the duplicate rows (should not display any rows)
if duplicate_rows.sum() > 0:
    print("Displaying duplicate rows:")
    print(df.loc[duplicate_rows, [Pollutant, 'Facility Name', 'Year']])

# Now, let us update the distance filtering to be dynamic based on the site
filter_site = 'Bronx (133)'  # You can change this to any site from your list to filter based on it
filter_distance = 100000  # You can change this to any distance you prefer

# Create a column for distances to the selected site
df['distance_to_site'] = df.apply(
    lambda row: great_circle(
        (row['Latitude'], row['Longitude']), 
        (site_coords[filter_site]['Latitude'], site_coords[filter_site]['Longitude'])
    ).miles, 
    axis=1
)

# Filter the data to include only points within the specified distance of the selected site
df = df[df['distance_to_site'] <= filter_distance]

# Filter by year
filter_by_year = True
start_year = 2021
end_year = 2021

if filter_by_year:
    df = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]

# Get the top 200 largest emitters based on the 'VOC (tons)' column
#Set the top 200 emitters
top_emitters = df.nlargest(100000, Pollutant) 

# Replace the data DataFrame with the top_emitters DataFrame
#Change to data=df if you want all emitters
data = top_emitters

# Find the maximum and minimum value in the 'VOC (tons)' column from the data without NaNs in 'VOC (tons)'
max_emission = data[Pollutant].max()
min_emission = data[Pollutant].min()

# Create a new column 'radius' by normalizing the 'VOC (tons)' column
data['radius'] = data[Pollutant].apply(lambda x: (x - min_emission) / (max_emission - min_emission) * 20 + 5)

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
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=row['radius'],  # Now using the normalized radius values
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.1,
        popup=f'<strong>Facility:</strong> {row["Facility Name"]}<br><strong>{Pollutant}:</strong> {row[Pollutant]}<br><strong>Year:</strong> {row["Year"]}',
    ).add_to(m)

# Add a heatmap to the map, excluding the NaN VOC (tons) values
heat_data = [[row['Latitude'], row['Longitude'], row[Pollutant]] for idx, row in data.iterrows() if not pd.isnull(row[Pollutant])]
HeatMap(heat_data).add_to(m)

# Create a new Marker Cluster with the filtered data
marker_cluster = MarkerCluster().add_to(m)

# Add bubbles to the map inside the marker cluster with the filtered data
for idx, row in data.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=row['radius'],  # Adjust the division value to change the radius size for clustering
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.1,
        popup=f'<strong>Facility:</strong> {row["Facility Name"]}<br><strong>{Pollutant}:</strong> {row[Pollutant]}<br><strong>Year:</strong> {row["Year"]}',
    ).add_to(marker_cluster)

# Save the map to an HTML file
m.save(r'C:\Users\LB945465\Desktop\bubble_map.html')
