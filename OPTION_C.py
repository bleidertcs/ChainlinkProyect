# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#Take monthly, daily, or meter data from Skyspark site and calculate baseline model

import pandas as pd
import eemeter
import eeweather
import numpy as np
from datetime import datetime, timedelta, timezone
#import datetime
import pytz
import csv
import os
import plotly.graph_objects as go
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
from dateutil import parser
import grafanalib



#######################Variables that need User Input#######################
#Specify lat/long for site
#extract temperature data for Houston
latitude = 25.9685577  #Houston loc
longitude = -80.1419707

#describe the frequency of billing data:
billing_freq = 'billing_monthly'
bldg_tz = 'US/Chicago'

#Read in .csv of   utility data
#filepath = 'C:\\Users\\bleider.colina\\Descargas\\OPTION_C_test.csv'
outfile = 'C:\\Users\\bleider.colina\\Downloads\\temp2.csv'

#meter_data, temperature_data, metadata = eemeter.load_sample('il-electricity-cdd-only-billing_monthly')

#specify start/stop time of baseline data
start_date = datetime(2018, 3, 1, tzinfo=pytz.UTC)
start_date.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M')
print('Start',start_date)
end_date = datetime(2020, 2, 5, tzinfo=pytz.UTC)
end_date.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M')
print('End',end_date)

eval_start_date = datetime(2020,5,1,tzinfo=pytz.UTC)
eval_end_date = datetime(2021,5,1,tzinfo=pytz.UTC)


#######################End Variables that need User Input#######################

ranked_stations_closest_within_climate_zone = eeweather.rank_stations(latitude,longitude,
                                                                     match_iecc_climate_zone=True,
                                                                     match_iecc_moisture_regime=True,
                                                                     match_ba_climate_zone=True,
                                                                     match_ca_climate_zone=True,
                                                                     max_distance_meters = 100000,
                                                                     is_tmy3 = True) #Choosing to use a station where TMY3 is available can increase distance significantly. Use with caution


#Use this table for timezone conversions
print(ranked_stations_closest_within_climate_zone)
selected_station, warnings = eeweather.select_station(
    ranked_stations_closest_within_climate_zone,
    coverage_range=(start_date, end_date))
print(selected_station)

temp_degC, warnings = selected_station.load_isd_hourly_temp_data(
    start_date, eval_end_date
)
print(temp_degC)

directory = os.getcwd()
filepath = directory + '\\temp.csv'

f = pd.read_csv(filepath,index_col=None)
print('file', f)
#date_time_obj = datetime.strptime(f["interval_start"], '%d/%m/%y %H:%M:%S')
#f["interval_start"] = pd.datetime.strptime(f["interval_start"], '%d/%m/%y %H:%M:%S')
#f["interval_end"] = pd.datetime.strptime(f["interval_end"], '%d/%m/%y %H:%M:%S')
#print('position 2',f['interval_start'][2])
f["interval_start"] = pd.to_datetime(f["interval_start"],format='%m/%d/%Y %H:%M')
#print('position 2', datetime.strptime(f["interval_start"][2], '%d/%m/%y %H:%M'))
f["interval_end"] = pd.to_datetime(f["interval_end"],format='%m/%d/%Y %H:%M')
print('position 2',f['interval_start'][2])

#Rename data frame columns
f.columns = ["start","end","value"]

column_names = f.columns

### Add a row that has a start date 1 day after last end date and an end date 2 days after end date and usage = NaN
#last_day = f["end"].tail(1)
last_day_pre = f.iloc[-1]
last_day = last_day_pre.end
delta = timedelta(days=1)
last_day_start = last_day + delta
last_day_end = last_day + delta*2

print('hola', column_names)

last_day_pre = f.iloc[-1]
last_day = last_day_pre.end
delta = timedelta(days=1)
last_day_start = last_day + delta
last_day_end = last_day + delta*2

#Make new data frame with fake entry
column_names = f.columns
f2 = pd.DataFrame([[last_day_start,last_day_end,np.nan]] ,columns = column_names, index = [(f.index[-1]+1)])
f2 = pd.DataFrame([[last_day_start,last_day_end,999]] ,columns = column_names, index = [(f.index[-1]+1)])

#Combine two data frames
f = pd.concat([f,pd.DataFrame(f2)],ignore_index=False)
f = f.append(f2)
print('Estado de f',f)

# Set "start" as the index column
f=f.set_index("start")

#drop the 2020 Usage column (just keep 2019 for nonw)
#f.drop(["2020 Usage"],axis=1,inplace = True)

#Set the final entry to NaN
#line = last_day
#f2 = pd.DataFrame([last_day,"NaN"],columns = column_names,index=[line])


#drop the end date column
f.drop(["end"],axis=1,inplace = True)



#remove "kwh from value column and convert to float"
#print(f["value"].str.lstrip('kWh'))
#f["value"] = f["value"].str.strip('kWh')

#remove commas from value column and convert to float"

f["value"]= str(f["value"]).replace(',','')
f["value"] = pd.to_numeric(f["value"],errors='coerce')
print(type(f["value"][0]))

#set last value to NaN as required by EEMeter
#f.loc[f.index[-1], 'value'] = np.nan

#write csv to be read in later by eemeter read option
f.to_csv(outfile,sep=',',mode="w+")
fnew = eemeter.meter_data_from_csv(outfile,start_col = "start", value_col = "value",gzipped = False)#, tz='UTC')
fnew = eemeter.meter_data_from_csv(outfile,start_col = "start", value_col = "value",gzipped = False, tz='UTC')

#describe the frequency of billing data:
fnew.freq = billing_freq
fnew.tz = bldg_tz

# get meter data suitable for fitting a baseline model
baseline_meter_data, warnings = eemeter.get_baseline_data(fnew, end=end_date, max_days=365)
print("baseline_meter_data is")
print(baseline_meter_data)
print(warnings)
print(fnew)
print(end_date)


# create a design matrix (the input to the model fitting step)
baseline_design_matrix = eemeter.create_caltrack_daily_design_matrix(
    baseline_meter_data, temp_degF,
)