from urllib import response
from flask import Flask, request, jsonify
import pandas as pd
import googlemaps
import csv
import requests
import os



app = Flask(__name__)

latitude = 29.76  #Houston loc
longitude = -95.38

#@app.get("/hola")
#def hola():
#    ranked_stations_closest_within_climate_zone = eeweather.rank_stations(latitude,longitude,
#                                                                     match_iecc_climate_zone=True,
#                                                                     match_iecc_moisture_regime=True,
#                                                                     match_ba_climate_zone=True,
#                                                                     match_ca_climate_zone=True,
#                                                                     max_distance_meters = 100000,
#                                                                     is_tmy3 = True)
#    print(ranked_stations_closest_within_climate_zone)
#    return jsonify('hola')

@app.post("/getUtilityData")
def findData():
    if request.is_json:
        data = request.get_json()
        id_meter = data["id_meter"]
        start_date = data["start_date"]
        end_date = data["end_date"]
        token = data["token"]
        filepath = utilityCall(id_meter, token)
        import_CSV(start_date, end_date, filepath)
        return "SUCCESS", 201
    
    return {"error": "Request must be JSON"}, 415

def utilityCall(meterId,token):
    ploads = {'meters':meterId,'access_token':token}
    directory = os.getcwd()
    
    with requests.Session() as s:
        download = s.get('https://utilityapi.com/api/v2/files/intervals_csv', params= ploads)
        fileName = 'utility.csv'
        contDownload = download.content
        csv_file = open(fileName, 'wb')
        csv_file.write(contDownload)
        csv_file.close()
        
    return directory + '\\' + fileName

def import_CSV(star_date, end_date, filepath):
    directory = os.getcwd()
    outfile = directory + '\\temp.csv'
    f = pd.read_csv(filepath, header=0, index_col=False) 
    filtered = f[['interval_start', 'interval_end', 'interval_kWh', 'meter_uid', 'utility_service_address']]
    csv_filtered_by_start_dates = filtered[filtered['interval_start']<=star_date]
    csv_filtered_by_end_dates = csv_filtered_by_start_dates[csv_filtered_by_start_dates['interval_end']>=end_date]
    #latitude = lat(csv_filtered_by_end_dates['utility_service_address'][0])
    #longitude = lon(csv_filtered_by_end_dates['utility_service_address'][0])
    #print('hola' + latitude)  
    csv_filtered_by_end_dates['latitude'] = csv_filtered_by_end_dates['utility_service_address'].apply(lat)
    csv_filtered_by_end_dates['longitude'] = csv_filtered_by_end_dates['utility_service_address'].apply(lon)
    csv_filtered_by_end_dates.to_csv(outfile,sep=',',mode="w+",index=False)

def lat(address):
    ##ApiKey
    gmaps_key = googlemaps.Client(key="")
    g = gmaps_key.geocode(address)
    lat = g[0]["geometry"]["location"]["lat"]
    return lat

def lon(address):
    ##ApiKey
    gmaps_key = googlemaps.Client(key="")
    g = gmaps_key.geocode(address)
    lon = g[0]["geometry"]["location"]["lng"]
    return lon
