import numpy as np
import datetime
from datetime import timezone
import requests
import time
import json
#! pip install geopy ##uncomment this if you don't have geopy installed
from geopy.geocoders import Nominatim
import pandas as pd

##################################################### Daily Data #############################################

key = "9bf841c7a680fd40c5f7d87b756a5e51" #open weather api key
city = "Kumasi"

url = "https://api.openweathermap.org/data/2.5/weather?q={cityname}&appid={APIkey}&units=metric".format(cityname = city,APIkey = key)

output = requests.get(url)

data = output.json()

###################################### Historical -  Past 5 Days Data #######################################

#sample cities and their corressponding geo cordi....

{"Accra" : {"latitude":5.603717,"longitude":-0.186964},
 "Kumasi":{"latitude":6.666600,"longitude":-1.616271},
 "Abuja":{"latitude",9.076479,"longitude",7.398574},
 "Lagos":{"latitude",6.524379,"longitude",3.379206}}


# Initialize Nominatim AP
geolocator = Nominatim(user_agent="MyApp")
location = geolocator.geocode("Lagos") #you can change the parameter of this method to any city of your choice...e.g Accra

location.latitude
location.longitude


def get_timestamp(y:int,m:int,d:int):
    """convert time to a Unix timestamp
    
    y:int  --> Year .e.g 2022
    m:int  --> Month, Month should be an inter of range 1 to 12 inclusive e.g. 3,indicating the month March 
    d:int  --> Day of the month; should be an integer
      
    stamp = get_timestamp(y = 2022,m = 3,d = 30)
    print(stamp)
    >>> 1648598400.0 """
    
    dt = datetime.datetime(y,m,d)
    #dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()
    return utc_timestamp


def make_request(lon,lat,stamp:int,unit:str = "metric",apikey:str = "9bf841c7a680fd40c5f7d87b756a5e51")->json:
    """get data for an entire day"""
    url = "https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={_lat_}&lon={_long_}&units={_unit_}&dt={_stamp_}&appid={_apikey_}".format(_lat_ = lat,_long_ = lon,_unit_ = unit,_stamp_ = int(stamp),_apikey_ = apikey)
    output=requests.get(url)
    return output.json()


def decode_Unix(timestamp):
    """convert timestands back to understandable time formats"""
    timestamp = datetime.datetime.fromtimestamp(1648735200)
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


def json_to_pandas(jsonfile: dict, dropna: bool = True) -> pd.DataFrame:
    """Extract Relevant Data from Json File and convert to Pandas DataFrame

    json:dict|json --> Input format json file format; the output after making a Request
    dropna:bool    --> A boolean any[True,False] - removes all NaN's from the dataframe; this will remove wind_gust and rain column

    Note : Not all columns in the Samples In the Json file have wind_gust and rain values"""

    df = pd.DataFrame(jsonfile['hourly'])  #
    df['zone'] = jsonfile['timezone'].split("/")[1] #get city 

    for i in range(len(df)):
        if i == 0:
            weather_data = pd.DataFrame(df["weather"][i])
        else:
            weather_data = pd.concat((weather_data, pd.DataFrame(df["weather"][i])), axis=0) 

    weather_data.reset_index(inplace=True, drop=True)

    df = df.join(weather_data, how="outer")
    df = df.dropna(axis=1) if dropna else df  # returns a DataFrame free of NaN's if dropna is specified as True
    df = df.drop(columns=['weather'], axis=1)  # drop weather after extracting features

    return df


if __name__=="__main__":
    stamp = get_timestamp(y=2022, m=3, d=30)
    print("Decoded Stamp: ",decode_Unix(stamp))
    output = make_request(location.longitude, location.latitude, stamp)
    json_to_pandas(output)



