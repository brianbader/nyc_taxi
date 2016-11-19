# Downloads yellow taxi data from NYC TLC dataset, described here:
# http://www.nyc.gov/html/tlc/html/about/trip_record_data.shtml
# WARNING: Very slow (each yellow file ~2GB)
# Compressed to about 1/4 the size in gzip format

# Years of data to download (currently 2009 - present)
years = ['2009', '2010', '2011', '2012', '2013', '2014', '2015']
# Months of data to download
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
# Can also add 'green' to the types list, beginning from August 2013
types = ['yellow']
url_add = 'https://s3.amazonaws.com/nyc-tlc/trip+data/'

import os, glob, pandas as pd
# Set to download directory
os.chdir('C:/Users/Beatrice/Desktop/Taxi Analysis/data')
# Get list of already downloaded files
files = glob.glob('yellow*')

for x in types:
    for y in years:
        for z in months:
            url_tmp = url_add + x + '_tripdata_' + y + '-' + z + '.csv'
            file_tmp = x + '_' + z + '_' + y + '.gz'
            if file_tmp not in files:
                tmp_data = pd.read_csv(url_tmp, error_bad_lines=False)
                tmp_data.to_csv(file_tmp, compression='gzip')
                print(file_tmp)
                del tmp_data