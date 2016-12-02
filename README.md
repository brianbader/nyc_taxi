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

## Plots
![alt text](https://github.com/geekman1/nyc_taxi/blob/master/plots/pickups_by_date.png "Total Pickups by Date and Type")

![alt text](https://github.com/geekman1/nyc_taxi/blob/master/plots/fares_by_date.png "Average Fares by Date and Type")

![alt text](https://github.com/geekman1/nyc_taxi/blob/master/plots/tips_by_date.png "Average Tips by Date and Type")



