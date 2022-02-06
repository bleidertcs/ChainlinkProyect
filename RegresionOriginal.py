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
from datetime import datetime, timedelta
#import datetime
import pytz
import csv
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dateutil import parser
import grafanalib



#######################Variables that need User Input#######################
#Specify lat/long for site
#extract temperature data for Houston
latitude = 29.76  #Houston loc
longitude = -95.38

#describe the frequency of billing data:
billing_freq = 'billing_monthly'
bldg_tz = 'US/Chicago'

#Read in .csv of   utility data
filepath = 'C:\\Users\\jbagley\\Downloads\\OPTION_C_test.csv'
outfile = 'C:\\Users\\jbagley\\Downloads\\temp.csv'

#meter_data, temperature_data, metadata = eemeter.load_sample('il-electricity-cdd-only-billing_monthly')

#specify start/stop time of baseline data
start_date = datetime(2018, 3, 1, tzinfo=pytz.UTC)
end_date = datetime(2020, 2, 5, tzinfo=pytz.UTC)
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
timezone_info = {
        "A": 1 * 3600,
        "ACDT": 10.5 * 3600,
        "ACST": 9.5 * 3600,
        "ACT": -5 * 3600,
        "ACWST": 8.75 * 3600,
        "ADT": 4 * 3600,
        "AEDT": 11 * 3600,
        "AEST": 10 * 3600,
        "AET": 10 * 3600,
        "AFT": 4.5 * 3600,
        "AKDT": -8 * 3600,
        "AKST": -9 * 3600,
        "ALMT": 6 * 3600,
        "AMST": -3 * 3600,
        "AMT": -4 * 3600,
        "ANAST": 12 * 3600,
        "ANAT": 12 * 3600,
        "AQTT": 5 * 3600,
        "ART": -3 * 3600,
        "AST": 3 * 3600,
        "AT": -4 * 3600,
        "AWDT": 9 * 3600,
        "AWST": 8 * 3600,
        "AZOST": 0 * 3600,
        "AZOT": -1 * 3600,
        "AZST": 5 * 3600,
        "AZT": 4 * 3600,
        "AoE": -12 * 3600,
        "B": 2 * 3600,
        "BNT": 8 * 3600,
        "BOT": -4 * 3600,
        "BRST": -2 * 3600,
        "BRT": -3 * 3600,
        "BST": 6 * 3600,
        "BTT": 6 * 3600,
        "C": 3 * 3600,
        "CAST": 8 * 3600,
        "CAT": 2 * 3600,
        "CCT": 6.5 * 3600,
        "CDT": -5 * 3600,
        "CEST": 2 * 3600,
        "CET": 1 * 3600,
        "CHADT": 13.75 * 3600,
        "CHAST": 12.75 * 3600,
        "CHOST": 9 * 3600,
        "CHOT": 8 * 3600,
        "CHUT": 10 * 3600,
        "CIDST": -4 * 3600,
        "CIST": -5 * 3600,
        "CKT": -10 * 3600,
        "CLST": -3 * 3600,
        "CLT": -4 * 3600,
        "COT": -5 * 3600,
        "CST": -6 * 3600,
        "CT": -6 * 3600,
        "CVT": -1 * 3600,
        "CXT": 7 * 3600,
        "ChST": 10 * 3600,
        "D": 4 * 3600,
        "DAVT": 7 * 3600,
        "DDUT": 10 * 3600,
        "E": 5 * 3600,
        "EASST": -5 * 3600,
        "EAST": -6 * 3600,
        "EAT": 3 * 3600,
        "ECT": -5 * 3600,
        "EDT": -4 * 3600,
        "EEST": 3 * 3600,
        "EET": 2 * 3600,
        "EGST": 0 * 3600,
        "EGT": -1 * 3600,
        "EST": -5 * 3600,
        "ET": -5 * 3600,
        "F": 6 * 3600,
        "FET": 3 * 3600,
        "FJST": 13 * 3600,
        "FJT": 12 * 3600,
        "FKST": -3 * 3600,
        "FKT": -4 * 3600,
        "FNT": -2 * 3600,
        "G": 7 * 3600,
        "GALT": -6 * 3600,
        "GAMT": -9 * 3600,
        "GET": 4 * 3600,
        "GFT": -3 * 3600,
        "GILT": 12 * 3600,
        "GMT": 0 * 3600,
        "GST": 4 * 3600,
        "GYT": -4 * 3600,
        "H": 8 * 3600,
        "HDT": -9 * 3600,
        "HKT": 8 * 3600,
        "HOVST": 8 * 3600,
        "HOVT": 7 * 3600,
        "HST": -10 * 3600,
        "I": 9 * 3600,
        "ICT": 7 * 3600,
        "IDT": 3 * 3600,
        "IOT": 6 * 3600,
        "IRDT": 4.5 * 3600,
        "IRKST": 9 * 3600,
        "IRKT": 8 * 3600,
        "IRST": 3.5 * 3600,
        "IST": 5.5 * 3600,
        "JST": 9 * 3600,
        "K": 10 * 3600,
        "KGT": 6 * 3600,
        "KOST": 11 * 3600,
        "KRAST": 8 * 3600,
        "KRAT": 7 * 3600,
        "KST": 9 * 3600,
        "KUYT": 4 * 3600,
        "L": 11 * 3600,
        "LHDT": 11 * 3600,
        "LHST": 10.5 * 3600,
        "LINT": 14 * 3600,
        "M": 12 * 3600,
        "MAGST": 12 * 3600,
        "MAGT": 11 * 3600,
        "MART": 9.5 * 3600,
        "MAWT": 5 * 3600,
        "MDT": -6 * 3600,
        "MHT": 12 * 3600,
        "MMT": 6.5 * 3600,
        "MSD": 4 * 3600,
        "MSK": 3 * 3600,
        "MST": -7 * 3600,
        "MT": -7 * 3600,
        "MUT": 4 * 3600,
        "MVT": 5 * 3600,
        "MYT": 8 * 3600,
        "N": -1 * 3600,
        "NCT": 11 * 3600,
        "NDT": 2.5 * 3600,
        "NFT": 11 * 3600,
        "NOVST": 7 * 3600,
        "NOVT": 7 * 3600,
        "NPT": 5.5 * 3600,
        "NRT": 12 * 3600,
        "NST": 3.5 * 3600,
        "NUT": -11 * 3600,
        "NZDT": 13 * 3600,
        "NZST": 12 * 3600,
        "O": -2 * 3600,
        "OMSST": 7 * 3600,
        "OMST": 6 * 3600,
        "ORAT": 5 * 3600,
        "P": -3 * 3600,
        "PDT": -7 * 3600,
        "PET": -5 * 3600,
        "PETST": 12 * 3600,
        "PETT": 12 * 3600,
        "PGT": 10 * 3600,
        "PHOT": 13 * 3600,
        "PHT": 8 * 3600,
        "PKT": 5 * 3600,
        "PMDT": -2 * 3600,
        "PMST": -3 * 3600,
        "PONT": 11 * 3600,
        "PST": -8 * 3600,
        "PT": -8 * 3600,
        "PWT": 9 * 3600,
        "PYST": -3 * 3600,
        "PYT": -4 * 3600,
        "Q": -4 * 3600,
        "QYZT": 6 * 3600,
        "R": -5 * 3600,
        "RET": 4 * 3600,
        "ROTT": -3 * 3600,
        "S": -6 * 3600,
        "SAKT": 11 * 3600,
        "SAMT": 4 * 3600,
        "SAST": 2 * 3600,
        "SBT": 11 * 3600,
        "SCT": 4 * 3600,
        "SGT": 8 * 3600,
        "SRET": 11 * 3600,
        "SRT": -3 * 3600,
        "SST": -11 * 3600,
        "SYOT": 3 * 3600,
        "T": -7 * 3600,
        "TAHT": -10 * 3600,
        "TFT": 5 * 3600,
        "TJT": 5 * 3600,
        "TKT": 13 * 3600,
        "TLT": 9 * 3600,
        "TMT": 5 * 3600,
        "TOST": 14 * 3600,
        "TOT": 13 * 3600,
        "TRT": 3 * 3600,
        "TVT": 12 * 3600,
        "U": -8 * 3600,
        "ULAST": 9 * 3600,
        "ULAT": 8 * 3600,
        "UTC": 0 * 3600,
        "UYST": -2 * 3600,
        "UYT": -3 * 3600,
        "UZT": 5 * 3600,
        "V": -9 * 3600,
        "VET": -4 * 3600,
        "VLAST": 11 * 3600,
        "VLAT": 10 * 3600,
        "VOST": 6 * 3600,
        "VUT": 11 * 3600,
        "W": -10 * 3600,
        "WAKT": 12 * 3600,
        "WARST": -3 * 3600,
        "WAST": 2 * 3600,
        "WAT": 1 * 3600,
        "WEST": 1 * 3600,
        "WET": 0 * 3600,
        "WFT": 12 * 3600,
        "WGST": -2 * 3600,
        "WGT": -3 * 3600,
        "WIB": 7 * 3600,
        "WIT": 9 * 3600,
        "WITA": 8 * 3600,
        "WST": 14 * 3600,
        "WT": 0 * 3600,
        "X": -11 * 3600,
        "Y": -12 * 3600,
        "YAKST": 10 * 3600,
        "YAKT": 9 * 3600,
        "YAPT": 10 * 3600,
        "YEKST": 6 * 3600,
        "YEKT": 5 * 3600,
        "Z": 0 * 3600,
}


#print out closest stations
#print(ranked_stations_closest_within_climate_zone.head(5))
###print("")

#Pull temperatur e data from closest station (Essentially pulls the USAF_id of the station)
selected_station, warnings = eeweather.select_station(
    ranked_stations_closest_within_climate_zone,
    coverage_range=(start_date, end_date))

temp_degC, warnings = selected_station.load_isd_hourly_temp_data(
    start_date, eval_end_date
)
temp_degF = temp_degC * 9 / 5 + 32
#Add frequency attribute to temperature dataframe
temp_degF.freq = 'hourly'



#meter_data, temperature_data, sample_metadata = (
#    eemeter.load_sample("il-electricity-cdd-hdd-hourly")
#)
#print(meter_data)



#print("selected station USAF_ID is: "+ selected_station.usaf_id)
#print("")

#Show information on selected station
####print(ranked_stations_closest_within_climate_zone.loc[selected_station.usaf_id])

f = pd.read_csv(filepath,index_col=None)

#Remove the -timezone portion of the ts column
#f["Timestamp"] = f["Timestamp"].str.slice(stop=25)

#Remove the : from the timezone offset
#f["Timestamp"] = f["Timestamp"].str.slice(stop=22)+f["Timestamp"].str.slice(start=23)

#Convert string to datetime
#temp = f["Timestamp"][0]

#f["Timestamp"] = pd.to_datetime(f["Timestamp"], format='%Y-%m-%dT%H:%M:%S%z')
f["Start Date (MM/DD/YYYY)"] = pd.to_datetime(f["Start Date (MM/DD/YYYY)"],format='%m/%d/%Y')
f["End Date (MM/DD/YYYY)"] = pd.to_datetime(f["End Date (MM/DD/YYYY)"],format='%m/%d/%Y')

#Rename data frame columns
f.columns = ["start","end","value"]

### Add a row that has a start date 1 day after last end date and an end date 2 days after end date and usage = NaN
#last_day = f["end"].tail(1)
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
#f = pd.concat([f,pd.DataFrame(f2)],ignore_index=False)
f = f.append(f2)

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
f["value"]= f["value"].str.replace(',','')
f["value"] = pd.to_numeric(f["value"],errors='coerce')
#print(type(f["value"][0]))

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
#print("baseline_meter_data is")
#print(baseline_meter_data)
#print(warnings)
#print(fnew)
#print(end_date)


# create a design matrix (the input to the model fitting step)
baseline_design_matrix = eemeter.create_caltrack_daily_design_matrix(
    baseline_meter_data, temp_degF,
)
#print((baseline_design_matrix.columns))

#Calculate days in each timestep and add it to the baseline_design_matrix dataframe
baseline_design_matrix['tvalue'] = baseline_design_matrix.index
baseline_design_matrix['delta'] = (baseline_design_matrix['tvalue'].shift(-1)-baseline_design_matrix['tvalue']).dt.days
print(baseline_design_matrix['tvalue'].shift(-1))
print(baseline_design_matrix['tvalue'])
print(baseline_design_matrix['delta'])


# build a CalTRACK model
baseline_model = eemeter.fit_caltrack_usage_per_day_model(
    baseline_design_matrix,fit_cdd=False,use_billing_presets=True,
    weights_col='delta'
)

#Get a year of reporting period data
reporting_meter_data, warnings = eemeter.get_reporting_data(fnew, start=eval_start_date, max_days=365)

#plot data time series
eemeter.plot_time_series(fnew, temp_degF)

#Compute metered savings for the year of the reporting period we've selected
metered_savings_dataframe, error_bands = eemeter.metered_savings(baseline_model,reporting_meter_data,
                                                                 temp_degF, with_disaggregated=True)

#Compute total savings for period:
total_metered_savings = metered_savings_dataframe.metered_savings.sum()

eemeter.plot_energy_signature(baseline_meter_data, temp_degF)
#list(baseline_design_matrix.columns)

ax = eemeter.plot_energy_signature(baseline_meter_data, temp_degF)
baseline_model.plot(ax=ax, with_candidates=True)

ax = eemeter.plot_energy_signature(baseline_meter_data, temp_degF)
baseline_model.plot(
    ax=ax, candidate_alpha=0.02, with_candidates=True, temp_range=(50, 88)
)
metered_savings_dataframe
#meter_data, temperature_data, sample_metadata = (
#    eemeter.load_sample("il-electricity-cdd-hdd-billing_monthly")
#)
#print(meter_data)
#print(sample_metadata)
#temp=meter_data.reset_index()
#print(temp)
#print(type(temp["start"][0]))
#print(temp_degF)
#print(fnew)
#Compute the temperature features corresponding to meter data dates
#hmm = eemeter.compute_temperature_features(fnew,temp_degF,temperature_mean=True,degree_day_method='hourly',
#                                           use_mean_daily_values=True)

baseline_meter_data
metered_savings_dataframe
