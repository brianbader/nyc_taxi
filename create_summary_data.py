# Summarizes / cleans the raw data to use in analysis. Only run this once!
# Creates four files:
# pickups_hd: total passengers by hour and day of week, sorted by rounded pickup lon/lat coords
# pickups_hr: total passengers by hour, sorted by rounded pickup lat/lon coords
# date_avgs: summaries (total passengers, total/avg fares, total/avg tips) by date
# pickups_hdl: total passengers by hour, date, and neighborhood (not lon/lat coords)
#######################################################
#######################################################

# Set location of top directory
top_dir = 'C:/Users/Beatrice/Desktop/Taxi Analysis'
# Set to number of decimals to round coordinates to
# 3 decimals provides ~ 100m resolution
num_dec = 3
import os, glob, pandas as pd, numpy as np
os.chdir(top_dir + '/data')
files = glob.glob('green*') + glob.glob('yellow*')
pd_locations = pd.read_pickle('pd_locs.pkl')

# Initialize empty dataframes to fill
# pickups_hd: pickups by hour, day of week, and rounded lon/lat
pickups_hd = pd.DataFrame(columns = ['passenger_count', 'day', 'hour', 'rounded_lon', 
                                     'rounded_lat', 'trip_time_in_secs', 'trip_distance'])
# pickups_hdl: pickups by date, hour, and neighborhood
pickups_hdl = pd.DataFrame(columns = ['passenger_count', 'date', 'hour', 'borough', 'nbhd'])

# date_avgs: overall trip summaries by date
date_avgs = pd.DataFrame(columns = ['passenger_count', 'date', 'fare_amount', 'tip_amount', 'trip_distance', 'type'])
date_counts = pd.DataFrame(columns = ['date', 'type', 0])

# running total of records
total_records = 0

for x in files:
    print(x)
    # Read in pickups files
    tmp = pd.read_csv(x)
    total_records += tmp.shape[0]
    tmp_col_names = [x.strip(' ').lower() for x in tmp.columns.values.tolist()]
    tmp_col_names = [x.replace('amt', 'amount') for x in tmp_col_names]
    tmp_col_names = [x.replace('start_lon', 'pickup_longitude') for x in tmp_col_names]
    tmp_col_names = [x.replace('start_lat', 'pickup_latitude') for x in tmp_col_names]
    tmp_col_names = ['pickup_time' if 'pickup_datetime' in x else x for x in tmp_col_names]
    tmp_col_names = ['dropoff_time' if 'dropoff_datetime' in x else x for x in tmp_col_names]
    tmp.columns = tmp_col_names
    tmp['rounded_lon'] = tmp.pickup_longitude.round(num_dec)
    tmp['rounded_lat'] = tmp.pickup_latitude.round(num_dec)
    tmp['trip_time_in_secs'] = (pd.to_datetime(tmp.dropoff_time, format='%Y-%m-%d %H:%M:%S') - 
                                pd.to_datetime(tmp.pickup_time, format='%Y-%m-%d %H:%M:%S')).dt.seconds
    tmp['day'] = pd.to_datetime(tmp.pickup_time, format='%Y-%m-%d %H:%M:%S').dt.dayofweek
    tmp['hour'] = pd.to_datetime(tmp.pickup_time, format='%Y-%m-%d %H:%M:%S').dt.hour
    tmp['date'] = pd.to_datetime(tmp.pickup_time, format='%Y-%m-%d %H:%M:%S').dt.date
    # Some data cleaning
    tmp = tmp[(tmp.passenger_count < 20) & (tmp.rounded_lon < -73) & (tmp.rounded_lat < 41) & 
              (0 < tmp.passenger_count)  & (-75 < tmp.rounded_lon) & (40 < tmp.rounded_lat) & 
              (0 < tmp.trip_time_in_secs) & (tmp.trip_time_in_secs < 7200) & (0 < tmp.fare_amount) & 
              (tmp.fare_amount < 200) & (0 < tmp.total_amount) & (tmp.total_amount < 200) & 
              (0 <= tmp.tip_amount) & (tmp.tip_amount < 200) & (0 < tmp.trip_distance) & 
              (tmp.trip_distance < 50)]
    # Remove trip speeds that may not make sense (trim top/bottom 1%)
    tmp = tmp[((tmp.trip_distance / tmp.trip_time_in_secs) < np.percentile((tmp.trip_distance / tmp.trip_time_in_secs), 99)) & 
              ((tmp.trip_distance / tmp.trip_time_in_secs) > np.percentile((tmp.trip_distance / tmp.trip_time_in_secs), 1))]
    tmp['type'] = 'green' if 'green' in x else 'yellow'
    # For pickups hour and day
    pickups_hd = pd.concat([pickups_hd, tmp[['passenger_count', 'day', 'hour', 'rounded_lon', 
                                             'rounded_lat', 'trip_time_in_secs', 'trip_distance']]], axis=0)
    pickups_hd = pickups_hd.groupby(['rounded_lon', 'rounded_lat', 'day', 
                                     'hour'])['passenger_count', 'trip_time_in_secs', 'trip_distance'].sum().reset_index()
    # For date averages, take sums and number of records by date
    date_avgs = pd.concat([date_avgs, tmp[['passenger_count', 'date', 'fare_amount', 'tip_amount', 'trip_distance', 'type']]], axis = 0)
    date_avgs = date_avgs.groupby(['date', 'type'])['passenger_count', 'fare_amount', 'tip_amount', 'trip_distance'].sum().reset_index()
    date_counts = pd.concat([date_counts, tmp.groupby(['date', 'type']).size().reset_index()], axis=0).groupby(['date', 'type'])[0].sum().reset_index()
    # For pickups date, hour, and neighborhood
    tmp = tmp[['passenger_count', 'date', 'hour', 'rounded_lon', 'rounded_lat']]
    tmp['passenger_count'] = tmp.groupby(['rounded_lon', 'rounded_lat', 'date', 'hour'])['passenger_count'].transform(sum)
    tmp.drop_duplicates(inplace=True)
    tmp = pd.merge(tmp, pd_locations, how='inner', on=['rounded_lon', 'rounded_lat'])
    tmp.drop(['rounded_lon', 'rounded_lat'], axis=1, inplace=True)
    tmp = tmp.groupby(['borough', 'nbhd', 'date', 'hour'])['passenger_count'].sum().reset_index()
    pickups_hdl = pd.concat([pickups_hdl, tmp], axis=0)
    pickups_hdl = pickups_hdl.groupby(['borough', 'nbhd', 'date', 'hour'])['passenger_count'].sum().reset_index()
    del tmp
    
## Remove points not in neighborhood boundaries
pickups_hd = pd.merge(pickups_hd, pd_locations, how='inner', on=['rounded_lon', 'rounded_lat'])
    
# Group by hour
pickups_hr = pickups_hd.groupby(by=['hour', 'rounded_lat', 
                                    'rounded_lon'])['passenger_count'].sum().reset_index()

# Summaries by date
date_avgs = pd.merge(date_avgs, date_counts, how='inner', on=['date', 'type'])
date_avgs.rename(columns={0:'total_pickups'}, inplace=True)
date_avgs.fare_amount = date_avgs.fare_amount / date_avgs.total_pickups
date_avgs.tip_amount = date_avgs.tip_amount / date_avgs.total_pickups
date_avgs.trip_distance = date_avgs.trip_distance / date_avgs.total_pickups

# Save to compressed file
pickups_hd.to_csv("pickups_hd.gz", compression="gzip")
pickups_hr.to_csv("pickups_hr.gz", compression="gzip")
date_avgs.to_csv("date_avgs.gz", compression="gzip")

#######################################################
#######################################################
# More processing on pickups by date, hour, and nbhd
# Add in zero pickup counts to those hour/date combinations 
# not returned from data
nbhd_list = pickups_hdl['nbhd'].unique().tolist()
date_list = pickups_hdl['date'].unique().tolist()
hour_list = pickups_hdl['hour'].unique().tolist()

from itertools import product
temp_fill = pd.DataFrame(list(product(nbhd_list, date_list, hour_list)), columns=['nbhd', 'date', 'hour'])
temp_fill['passenger_count'] = 0
temp_fill = pd.merge(temp_fill, pickups_hdl[['nbhd', 'borough']].drop_duplicates(), 
                     how='left', on='nbhd')

pickups_hdl = pd.concat([pickups_hdl, temp_fill], axis=0)
pickups_hdl = pickups_hdl.groupby(['borough', 
                                   'nbhd', 'date', 'hour'])['passenger_count'].sum().reset_index()

# Merge weather and holiday info!
# Import weather data (JFK airport, obtained here: 
# https://www.wunderground.com/history/airport/KJFK)
weather = pd.read_csv('jfk_weather.csv')
weather.EST = pd.to_datetime(weather.EST, format='%m/%d/%Y')
pickups_hdl.date = pd.to_datetime(pickups_hdl.date, format='%Y-%m-%d')

# Check if date falls on a US holiday
from pandas.tseries.holiday import USFederalHolidayCalendar as calendar
cal = calendar()
holidays = cal.holidays(start=pickups_hdl.date.min(), end=pickups_hdl.date.max())
pickups_hdl['holiday'] = pickups_hdl.date.isin(holidays).astype(int)

# Join weather data w/ pickups (by date)
pickups_hdl = pd.merge(pickups_hdl, weather, how='left', left_on=['date'], right_on=['EST'])
pickups_hdl['day_of_week'] = pickups_hdl['date'].dt.dayofweek
pickups_hdl['month'] = pickups_hdl['date'].dt.month
pickups_hdl.drop(['EST'], axis=1, inplace=True)

# Save to compressed file
pickups_hdl.to_csv("pickups_hdl.gz", compression="gzip")