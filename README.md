# nyc_taxi
Analysis of NYC taxi trip data

This repository provides Python code to analyze New York City taxi pickups from 2009 - present (currently through June 2016). A detailed description of the data is available [here](http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml), as well as the actual data in CSV format. The directory should be set up as follows:

- Top Directory (called 'Taxi Analysis' in the code)
  - Top Directory\plots
  - Top Directory\data
  
Make sure to download the 'nyc_neighborhoods.json' file to the top folder and the 'jfk_weather.csv' to the data subfolder. These contain the GeoJSON data for New York City neighborhoods (polygon boundaries) and daily weather data for JFK airport over the timeframe of the taxi pickup data. The Python scripts should be run in the following order (make sure to update the top directory location path in each):
  
1. data_download.py (Downloads the trip data and saves to compressed gzip format files in the data directory. Requires ~40GB of disk space.)
2. find_nbhd_centroids_boundaries.py (Finds and saves the neighborhood centroids and borders from the NYC neighborhoods JSON file.)
3. find_pickup_dropoff_nbhds.py (Finds the neighborhood and borough of each pickup and dropoff location in the full dataset by reverse geocoding the longitude/latitude coordinate pairs using the GeoJSON NYC neighborhoods file.)
4. create_summary_data.py (Creates summarized datasets to use for descriptive plots and modeling.)
5. nyc_taxi_analysis.py (Creates plots, data summaries, and fits a predictive model for pickup frequencies.)


# Plots
![alt text](https://github.com/geekman1/nyc_taxi/blob/master/plots/pickups_by_date.png "Total Pickups by Date and Type")

![alt text](https://github.com/geekman1/nyc_taxi/blob/master/plots/fares_by_date.png "Average Fares by Date and Type")

![alt text](https://github.com/geekman1/nyc_taxi/blob/master/plots/tips_by_date.png "Average Tips by Date and Type")

The next plot shows the percent change in total annual number of pickups for 2015 compared to 2010, by neighborhood.

![alt text](https://github.com/geekman1/nyc_taxi/blob/master/plots/2010_2015_percent_change.png "2010 to 2015 Percent Change in Pickups by Neighborhood")

|   percent_change | nbhd               | borough   |
|-----------------:|:-------------------|:----------|
|         16.2  | Coney Island       | Brooklyn  |
|         14.6   | Marble Hill        | Manhattan |
|         13.9  | Pelham Bay         | Bronx     |
|         12.2 | Norwood            | Bronx     |
|         11.3  | Bedford-Stuyvesant | Brooklyn  |
|         10.8  | Melrose            | Bronx     |
|         10.7  | Kew Gardens        | Queens    |
|          9.8 | Belmont            | Bronx     |
|          9.6 | Crown Heights      | Brooklyn  |
|          9.2 | Jackson Heights    | Queens    |

Shown next are the relative proportions of late night pickups by neighborhood (late night defined as the time frame from 10pm to 3am), with the top ten shown below.

![alt text](https://github.com/geekman1/nyc_taxi/blob/master/plots/late_night_pickups.png "Relative Proportion of Late Night Pickups by Neighborhood")

|   relative_percent | nbhd             | borough   |
|-------------------:|:-----------------|:----------|
|            52.9 | Bushwick         | Brooklyn  |
|            52.6 | Williamsburg     | Brooklyn  |
|            45.0  | Lower East Side  | Manhattan |
|            44.6 | Greenpoint       | Brooklyn  |
|            41.5  | Nolita           | Manhattan |
|            41.3 | Park Slope       | Brooklyn  |
|            41.3 | South Slope      | Brooklyn  |
|            41.0 | Prospect Heights | Brooklyn  |
|            39.3 | Ridgewood        | Queens    |
|            37.3 | Crown Heights    | Brooklyn  |


# Predicting Taxi Pickups Frequencies by Neighborhood Using Random Forests

It would be of interest to taxi dispatchers to be able to predict the frequency of pickups by location. The following shows the true frequency of taxi pickups (by latitude / longitude pair rounded to three digits), by hour from January 2009 - June 2016. It's quite beautiful, and you can clearly see the ebb and flow of airport pickups (particularly JFK).

![alt text](https://github.com/geekman1/nyc_taxi/blob/master/plots/pickups_movie.gif "Actual Pickups by Hour, Location")

Instead of attempting to predict pickups at each latitude / longitude location, pickup totals are aggregated by neighborhood and the goal is to predict neighborhood pickup totals at a particular hour and date. Data from 2014 is used to predict the number of pickups at every neighborhood for each hour and date in 2015. As a baseline measure, the most naive guess is to use the actual pickups in 2014 to predict the number of pickups in 2015 (by date, hour, and neighborhood). This provides an R^2 value of 91.0 and mean squared error of 32,438.5.

To compare, a random forest (RF) model is built to make predictions. This has the advantage over the naive approach as it can incorporate covariates and compared to other predictive models, can accomodate non-linear relationships between the predictors and outcome (pickup totals). For covariates, daily weather data from JFK airport is used, as well as hour, day of week, month, holiday indication, and neighborhood. A subset of the 2014 data is used to tune the RF parameters via a random search, and predicting on out of sample data from 2015. The tuning parameters which give the best performance are then used to fit a RF to the full 2014 data, to predict total pickups for each hour, neighborhood, and date in 2015. This gives an R^2 value of 95.0 and mean squared error of 14,250.8 (less than 50% of the naive approach). The actual versus predicted total daily pickups by neighborhood for a random date (May 7th, 2015) is shown below.

![alt text](https://github.com/geekman1/nyc_taxi/blob/master/plots/actual_pred_pickups.png "Actual vs. Predicted Total Pickups on May 7, 2015 by NYC Neighborhood")

## Improvements / Thoughts

- Additional covariates can be added to improve the error of the model. A few that come to mind are population density (by neighborhood), more granular weather data (hourly), and some sort of seasonality measure.
- Other supervised learning models may provide better performance than RF. It may be worthwhile to do a comparison.
- Other evaluation metrics can be used, such as Mean Squared Logarithmic Error. However, this increases the penalty on deviations in neighborhoods with small pickup totals, which may not be an appropriate in this situation. For example, a prediction of 2 pickups for a neighborhood with 1 actual pickup gives approximately the same penalty as predicting 1500 pickups for a neighborhood with 1000 actual pickups.
