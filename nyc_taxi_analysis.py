# Documentation / info about the dataset is contained here
# http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml
# https://cloud.google.com/bigquery/public-data/nyc-tlc-trips
#################################################################
#################################################################

# Change this path to point to your top directory
top_dir = 'C:/Users/Beatrice/Desktop/Taxi Analysis'

#################################################################
#################################################################
################ DESCRIPTIVE PLOTS ##############################
#################################################################
#################################################################

import os, pandas as pd, numpy as np, random
from rpy2 import robjects
from rpy2.robjects.lib import ggplot2
from rpy2.robjects import pandas2ri
from tabulate import tabulate
%load_ext rpy2.ipython
%R require('ggplot2')
pandas2ri.activate()
# Set random seed
random.seed(7)

os.chdir(top_dir)
pickups_hd = pd.read_csv('./data/pickups_hd.gz')
pickups_hr = pd.read_csv('./data/pickups_hr.gz')
pickups_hdl = pd.read_csv('./data/pickups_hdl.gz')
pickups_hdl['date'] = pd.to_datetime(pickups_hdl.date, format='%Y-%m-%d')
pickups_hdl['year'] = pickups_hdl.date.dt.year
date_avgs = pd.read_csv('./data/date_avgs.gz')
date_avgs['date'] = pd.to_datetime(date_avgs.date, format='%Y-%m-%d')
pd_locs = pd.read_pickle('./data/pd_locs.pkl')
nbhd_borders = pd.read_pickle('./data/nbhd_borders.pkl')

# Average speed by borough
borough_speed = pickups_hd.groupby(['borough'])['trip_time_in_secs', 'trip_distance'].sum().reset_index()
borough_speed['mph'] = 3600 * (borough_speed.trip_distance / borough_speed.trip_time_in_secs)
borough_speed

# Average speed by day, hour
hour_speed = pickups_hd.groupby(['day', 'hour'])['trip_time_in_secs', 'trip_distance'].sum().reset_index()
hour_speed['mph'] = 3600 * (hour_speed.trip_distance / hour_speed.trip_time_in_secs)
hour_speed
   
# Pickups by hour (aggregated across all days)
max_passenger_count = np.max(np.log1p(pickups_hr['passenger_count']))
min_passenger_count = np.log1p(1)

for i in range(0,24):
        temp = pickups_hr[(pickups_hr.hour==i)].reset_index()
        temp.passenger_count = np.log1p(temp.passenger_count)
        temp_r = pandas2ri.py2ri(temp)
        p = ggplot2.ggplot(temp_r) + \
            ggplot2.aes_string(x='rounded_lon', y='rounded_lat', color='passenger_count') + \
            ggplot2.geom_point(size=0.5) + \
            ggplot2.scale_color_gradient(low='black', high='white', limits=np.array([min_passenger_count, max_passenger_count])) + \
            ggplot2.xlim(-74.2, -73.7) + ggplot2.ylim(40.56, 40.93) + \
            ggplot2.labs(x=' ', y=' ', title='NYC taxi pickups %02i:00' % i) + \
            ggplot2.guides(color=False)
        p.save('./plots/taxi_pickups%02i.png' % i, width=4, height=4.5)
        
# Create animated .gif of pickups by hour
import imageio

file_names = sorted((fn for fn in os.listdir('./plots') if fn.startswith('taxi_pickups')))
file_names = ['plots/' + s for s in file_names]
images = []
for filename in file_names:
    images.append(imageio.imread(filename))
imageio.mimsave('./plots/pickups_movie.gif', images, duration=0.4)

# total pickups by date, color
p1 = ggplot2.ggplot(pandas2ri.py2ri(date_avgs)) + \
ggplot2.aes_string(x='date', y='total_pickups', color='type') + \
ggplot2.scale_colour_manual(values = robjects.StrVector(['green', 'yellow'])) + \
ggplot2.geom_line() + \
ggplot2.theme(legend_position='bottom') + \
ggplot2.labs(y='Total Pickups', x='Date', title='Total Pickups by Date')
p1.save('./plots/pickups_by_date.png', width=6, height=5)

# average fare and tip by date, color
p2 = ggplot2.ggplot(pandas2ri.py2ri(date_avgs)) + \
ggplot2.aes_string(x='date', y='fare_amount', color='type') + \
ggplot2.scale_colour_manual(values = robjects.StrVector(['green', 'yellow'])) + \
ggplot2.geom_line() + \
ggplot2.theme(legend_position='bottom') + \
ggplot2.labs(y='Average Fare ($)', x='Date', title='Average Fare by Date')
p2.save('./plots/fares_by_date.png', width=6, height=5)

p3 = ggplot2.ggplot(pandas2ri.py2ri(date_avgs)) + \
ggplot2.aes_string(x='date', y='tip_amount', color='type') + \
ggplot2.scale_colour_manual(values = robjects.StrVector(['green', 'yellow'])) + \
ggplot2.geom_line() + \
ggplot2.theme(legend_position='bottom') + \
ggplot2.labs(y='Average Tip ($)', x='Date', title='Average Tip by Date')
p3.save('./plots/tips_by_date.png', width=6, height=5)

# Plot late night % of pickups by neighborhood
pickups_late = pd.merge(pickups_hd, pd_locs, 
                        how='inner', on=['rounded_lon', 'rounded_lat', 'borough', 'nbhd'])

# Group by late, not late in each neighborhood
pickups_late['period'] = np.where(pickups_late['hour'].isin([22, 23, 0, 1, 2]), 'late', 'not late')
pickups_late = pickups_late.groupby(['nbhd', 'period'])['passenger_count'].sum().reset_index()

temp_perc = pickups_late.groupby(['nbhd'])['passenger_count'].apply(lambda x: 100*x/float(x.sum())).reset_index()
temp_perc = temp_perc.rename(columns={'passenger_count':'relative_percent'})
pickups_late = pd.concat([pickups_late, temp_perc['relative_percent']], axis=1)
pickups_late = pickups_late[pickups_late['period'] == 'late']
pickups_late = pd.merge(pickups_late, nbhd_borders, how='right', on=['nbhd']).dropna()

# Find top 10 neighborhoods with largest late night % of pickups
print(tabulate(pickups_late[['relative_percent', 'nbhd', 
                             'borough']].drop_duplicates().sort(['relative_percent'], ascending=False).head(10), 
                             tablefmt='pipe', headers='keys', showindex=False))

p4 = ggplot2.ggplot(pandas2ri.py2ri(pickups_late)) + \
ggplot2.aes_string(x='lon', y='lat', group='nbhd', fill='relative_percent') + \
ggplot2.geom_polygon() + \
ggplot2.theme(legend_position='bottom') + \
ggplot2.labs(x='', y='', title='Late Night Pickups (% of All Pickups)')
p4.save('./plots/late_night_pickups.png', width=5, height=6)

# Plot % change (2010 to 2015) in pickups by neighborhood
pickups_change = pickups_hdl.groupby(['nbhd', 'borough', 'year'])['passenger_count'].sum().reset_index()
pickups_change = pickups_change[pickups_change['year'].isin([2010, 2015])].reset_index()
pickups_change = pickups_change.sort_values(['nbhd', 'year']).reset_index()
temp_change = pickups_change.groupby(['nbhd'])['passenger_count'].apply(lambda x: x.pct_change()).reset_index()
temp_change = temp_change.rename(columns={'passenger_count':'percent_change'})
pickups_change = pd.concat([pickups_change, temp_change['percent_change']], axis=1)
pickups_change = pickups_change.dropna()

# Find top 10 neighborhoods with largest percent change
print(tabulate(pickups_change[['percent_change', 'nbhd', 
                               'borough']].drop_duplicates().sort(['percent_change'], ascending=False).head(10), 
                               tablefmt='pipe', headers='keys', showindex=False))

pickups_change['percent_change'] = np.log1p(pickups_change['percent_change'] + abs(min(pickups_change['percent_change'])))
pickups_change = pd.merge(pickups_change, nbhd_borders, how='right', on=['nbhd']).dropna()

p5 = ggplot2.ggplot(pandas2ri.py2ri(pickups_change)) + \
ggplot2.aes_string(x='lon', y='lat', group='nbhd', fill='percent_change') + \
ggplot2.geom_polygon() + \
ggplot2.scale_fill_gradient(low='blue', high='green') + \
ggplot2.theme(legend_position='bottom') + \
ggplot2.labs(x='', y='', title='Change In Annual # of Pickups (2010 - 2015)', fill='Percent Change\n(Log-Scale)')
p5.save('./plots/2010_2015_percent_change.png', width=5, height=6)


#################################################################
#################################################################
################ MODEL FITTING ##################################
#################################################################
#################################################################

# Do some quick benchmarks (predict 2015 from 2014 data)
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint as sp_randint
from sklearn.metrics import mean_squared_error, r2_score

pickups_14_15 = pickups_hdl[pickups_hdl['year'].isin([2014, 2015])]

# Data cleaning
# Remove NAs and non-informative data
pickups_14_15_col_names = pickups_14_15.columns.values.tolist()
pickups_14_15.columns = [x.strip(' ') for x in pickups_14_15_col_names]
pickups_14_15['PrecipitationIn'] = pickups_14_15.PrecipitationIn.str.replace('T', '0')
pickups_14_15.PrecipitationIn = pickups_14_15.PrecipitationIn.apply(pd.to_numeric, errors='coerce')
pickups_14_15.drop(['Unnamed: 0', 'CloudCover', 'Events', 'WindDirDegrees'], axis=1, inplace=True)
pickups_14_15.dropna(inplace=True)

# Find invalid dates in both 2014 and 2015 (those without weather info)
dates_2014 = pickups_14_15[pickups_14_15.year == 2014].date.apply(lambda x: x.strftime('%m-%d'))  
dates_2015 = pickups_14_15[pickups_14_15.year == 2015].date.apply(lambda x: x.strftime('%m-%d'))  
dates_intersect = set.intersection(set(dates_2014), set(dates_2015))
pickups_14_15 = pickups_14_15[pickups_14_15.date.apply(lambda x: x.strftime('%m-%d')).isin(dates_intersect)]
pickups_14_15 = pickups_14_15.sort_values(['nbhd', 'date', 'hour']).reset_index()

# Check MSE and R^2 of naive approach
mean_squared_error(pickups_14_15[pickups_14_15.year == 2014]['passenger_count'], 
                   pickups_14_15[pickups_14_15.year == 2015]['passenger_count'])

r2_score(pickups_14_15[pickups_14_15.year == 2014]['passenger_count'], 
                   pickups_14_15[pickups_14_15.year == 2015]['passenger_count'])

# Split data into train/test by year
pickups_14_15['day_of_week'] = pickups_14_15['day_of_week'].apply(str)
pickups_14_15['hour'] = pickups_14_15['hour'].apply(str)
pickups_14_15['month'] = pickups_14_15['month'].apply(str)

# Create training data (2014)
X_train = pickups_14_15[pickups_14_15['year'] == 2014]
Y_train = X_train['passenger_count']
X_train.drop(['date', 'passenger_count', 'year'], axis=1, inplace=True)
X_train = pd.get_dummies(X_train)

# Try random forest model, randomized search for optimal parameters
rf = RandomForestRegressor()
# Specify parameters and distributions to sample from
param_dist = {'n_estimators': sp_randint(1, 101),
              'max_depth': [1, 2, 3, None],
              'max_features': sp_randint(1, X_train.shape[1]),
              'min_samples_split': sp_randint(1, 11),
              'min_samples_leaf': sp_randint(1, 11),
              'bootstrap': [True, False]}

# Run randomized search
# Try it on subset of training data to speed up search
sample_index = X_train.sample(50000).index
n_iter_search = 50
random_search = RandomizedSearchCV(rf, param_distributions=param_dist, n_iter=n_iter_search)
random_search.fit(X_train.ix[sample_index], Y_train.ix[sample_index])
random_search.best_params_

# Create test data (2015)
X_test = pickups_14_15[pickups_14_15['year'] == 2015]
Y_test = X_test['passenger_count']
X_test.drop(['date', 'passenger_count', 'year'], axis=1, inplace=True)
X_test = pd.get_dummies(X_test)

# Use 'best' parameters from the random_search output
# to train the full 2014 data
rf = RandomForestRegressor(n_estimators=random_search.best_params_['n_estimators'], 
                           max_depth=random_search.best_params_['max_depth'], 
                           max_features=random_search.best_params_['max_features'], 
                           min_samples_leaf=random_search.best_params_['min_samples_leaf'], 
                           min_samples_split=random_search.best_params_['min_samples_split'], 
                           bootstrap=random_search.best_params_['bootstrap'])
rf.fit(X_train, Y_train)

# Check MSE and R^2 of RF approach
mean_squared_error(Y_test, rf.predict(X_test))
r2_score(Y_test, rf.predict(X_test))

# Prepare the RF output to be plotted
pickups_2015_actual = pickups_14_15[pickups_14_15['year'] == 2015][['borough', 'nbhd', 'date', 'hour', 'passenger_count']]
pickups_2015_pred = pickups_2015_actual.copy()
pickups_2015_pred['passenger_count'] = rf.predict(X_test)
pickups_2015_actual['type'] = 'actual'
pickups_2015_pred['type'] = 'predicted'
pickups_2015 = pd.concat([pickups_2015_actual, pickups_2015_pred], axis=0)
pickups_2015 = pickups_2015.groupby(['borough', 'nbhd', 'date', 'type'])['passenger_count'].sum().reset_index()
# Pick a random date to look at
pickups_2015 = pickups_2015[pickups_2015['date'] == '2015-05-07']
pickups_2015 = pd.merge(pickups_2015, nbhd_borders, how='right', on=['nbhd']).dropna()
pickups_2015['passenger_count'] = np.log1p(pickups_2015['passenger_count'])

# Plot actual vs. predicted
p6 = ggplot2.ggplot(pandas2ri.py2ri(pickups_2015)) + \
ggplot2.aes_string(x='lon', y='lat', group='nbhd', fill='passenger_count') + \
ggplot2.geom_polygon() + \
ggplot2.facet_wrap(robjects.Formula('~ type')) + \
ggplot2.scale_fill_gradient(low='yellow', high='red') + \
ggplot2.theme(legend_position='bottom') + \
ggplot2.labs(x='', y='', title='Actual vs. Expected Total Passengers on 5-7-2015', fill='Passenger Count\n(Log-Scale)')
p6.save('./plots/actual_pred_pickups.png', width=7, height=5)