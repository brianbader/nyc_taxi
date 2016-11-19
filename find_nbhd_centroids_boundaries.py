import os, json, pandas as pd
from shapely.geometry import Polygon
# Set top directory
top_dir = top_dir = 'C:/Users/Beatrice/Desktop/Taxi Analysis'
os.chdir(top_dir)

# load JSON file containing neighborhood sectors
with open('nyc_neighborhoods.json', 'r') as f:
    js = json.load(f)

###################################################################
###################################################################
# Finds nbhd centroids for each nbhd in the JSON file
lon = []
lat = []
nbhd = []
brgh = []

for feature in js['features']:
    lon.append(Polygon(feature['geometry']['coordinates'][0]).centroid.x)
    lat.append(Polygon(feature['geometry']['coordinates'][0]).centroid.y)
    nbhd.append(feature['properties']['neighborhood'])
    brgh.append(feature['properties']['borough'])
    
nbhd_centroids = pd.DataFrame({'lon': lon, 'lat': lat, 'nbhd': nbhd, 'borough': brgh})
nbhd_centroids = nbhd_centroids.loc[nbhd_centroids[['borough', 'nbhd']].drop_duplicates().index]
nbhd_centroids.to_pickle('./data/nbhd_centroids.pkl')

###################################################################
###################################################################
# Create dataframe of neighborhood border points (from JSON file)
lon = []
lat = []
nbhd = []
brgh = []

for feature in js['features']:
    lon.extend([x[0] for x in feature['geometry']['coordinates'][0]])
    lat.extend([x[1] for x in feature['geometry']['coordinates'][0]])
    nbhd.extend([feature['properties']['neighborhood']] * len(feature['geometry']['coordinates'][0]))
    brgh.extend([feature['properties']['borough']] * len(feature['geometry']['coordinates'][0]))
    
nbhd_borders = pd.DataFrame({'lon': lon, 'lat': lat, 'nbhd': nbhd, 'borough': brgh})
nbhd_borders = nbhd_borders.drop_duplicates()
nbhd_borders.to_pickle('./data/nbhd_borders.pkl')