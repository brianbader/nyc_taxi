# Code to recover neighborhood / borough info from lat/lon coords
# Finds neighborhood / borough info for all possible pickup/dropoff locations
# Need to round lat/lon coords to speed up lookups
# Only run this once!
####################################################################
####################################################################
# Make sure to download this file (or pull file 'nyc_neighborhoods.json' from GitHub):
# http://data.beta.nyc//dataset/0ff93d2d-90ba-457c-9f7e-39e47bf2ac5f/resource/35dd04fb-81b3-479b-a074-a27a37888ce7/download/d085e2f8d0b54d4590b1e7d1f35594c1pediacitiesnycneighborhoods.geojson
# Save it as 'nyc_neighborhoods.json' in top directory
####################################################################
####################################################################
# Set this to top directory
top_dir = 'C:/Users/Beatrice/Desktop/Taxi Analysis'
# Set to number of decimals to round coordinates to
# 3 decimals provides ~ 100m resolution
num_dec = 3

import os, glob, pandas as pd, numpy as np
os.chdir(top_dir + '/data')
files = glob.glob('green*') + glob.glob('yellow*')
pd_locations = pd.DataFrame(columns = ['rounded_lon', 'rounded_lat'])

# Collect all unique rounded pickup/dropoff coords
for x in files:
    tmp = pd.read_csv(x)
    # Clean header names of some files
    tmp_col_names = [x.strip(' ').lower() for x in tmp.columns.values.tolist()]
    tmp_col_names = [x.replace('amt', 'amount') for x in tmp_col_names]
    tmp_col_names = [x.replace('start_lon', 'pickup_longitude') for x in tmp_col_names]
    tmp_col_names = [x.replace('start_lat', 'pickup_latitude') for x in tmp_col_names]
    tmp_col_names = [x.replace('end_lon', 'dropoff_longitude') for x in tmp_col_names]
    tmp_col_names = [x.replace('end_lat', 'dropoff_latitude') for x in tmp_col_names]
    tmp.columns = tmp_col_names
    tmp1 = tmp[['pickup_longitude', 'pickup_latitude']].round(num_dec)
    tmp2 = tmp[['dropoff_longitude', 'dropoff_latitude']].round(num_dec)
    tmp1.columns = ['rounded_lon', 'rounded_lat']
    tmp2.columns = ['rounded_lon', 'rounded_lat']
    tmp_locs = pd.concat([tmp1, tmp2], ignore_index=True)
    tmp_locs.drop_duplicates(inplace=True)
    pd_locations = pd.concat([pd_locations, tmp_locs], ignore_index=True)
    pd_locations.drop_duplicates(inplace=True)
    print(x)
    del tmp, tmp1, tmp2, tmp_locs

# Change back to top directory
os.chdir(top_dir)

# Drop NAs, sort coords to make lookups faster
pd_locations.dropna(inplace=True)
pd_locations = pd_locations.sort(['rounded_lon', 'rounded_lat']).reset_index()[['rounded_lon', 'rounded_lat']]

# Do geohashing to borough and neighborhood
import json
from shapely.geometry import shape, Point
# load GeoJSON file containing neighborhood sectors, discussed on lines 7-9
with open('nyc_neighborhoods.json', 'r') as f:
    js = json.load(f)
      
# Create some heuristic boundaries based on min/max coords of all polygons 
poly_bounds = np.empty((0))
for feature in js['features']:
    check_coords = feature['geometry']['coordinates'][0]
    poly_bounds = np.append(poly_bounds, [item for item in check_coords])
poly_bounds = poly_bounds.flatten()
poly_minlat = min(poly_bounds[poly_bounds > 0])
poly_maxlat = max(poly_bounds[poly_bounds > 0])
poly_minlon = min(poly_bounds[poly_bounds < 0])
poly_maxlon = max(poly_bounds[poly_bounds < 0])

# initialize some things for the loop
l1 = []
l2 = []
feature = js['features'][0]

# check each polygon to see if it contains the point
# try the previous point's nbhd first, since the points are sorted
for x, row1 in pd_locations.iterrows():
    temp_point = Point(pd_locations.rounded_lon[x], pd_locations.rounded_lat[x])
    l1.append(np.nan)
    l2.append(np.nan)
    if(x%1000 == 0):
        print(str(x) + ' rows processed...')
    if(poly_minlon < pd_locations.rounded_lon[x] < poly_maxlon) and (poly_minlat < pd_locations.rounded_lat[x] < poly_maxlat):
        temp_polygon = shape(feature['geometry'])
        if temp_polygon.contains(temp_point):
            l1[x] = feature['properties']['borough']
            l2[x] = feature['properties']['neighborhood']
        else:
            for feature in js['features']:
                polygon = shape(feature['geometry'])
                if polygon.contains(temp_point):
                    l1[x] = feature['properties']['borough']
                    l2[x] = feature['properties']['neighborhood']
                    break

pd_locations['borough'] = l1
pd_locations['nbhd'] = l2

pd_locations = pd_locations.dropna().reset_index(drop=True)
# save file to pickle as pd_locs.pkl
pd_locations.to_pickle('./data/pd_locs.pkl')