
# Use SoilGrids and APIXU APIs to retrieve soil and recent weather for a location
#
# Meaningless change to test working with GitHub

# SoilGrids: Info at https://rest.soilgrids.org/query.html
# APIXU: info at https://www.apixu.com/doc/request.aspx

# Written for Python 3.5

# Stewart Marshall 20/01/2017
# 02/2017 Tried aWhere for weather but unsuitable data model 
# 02/2017 Added APIXU for weather, refactored and added work over date range 

import sys
import requests
from pprint import pprint
from datetime import datetime, timedelta


def retrieveSoilGridsData(latitude,longitude):

    domain = "rest.soilgrids.org"
    route = "query"
    url = "https://%s/%s" % (domain,route)

    # Specify organic carbon and CEC only in response
    #soilProperties = "ORCDRC,CEC"
    #payload = {"lat" : latitude, "lon" : longitude, "attributes" : soilProperties }

    payload = {"lat" : latitude, "lon" : longitude}

    try:
        response = requests.get(url, params = payload)

    except requests.exceptions.ConnectionError as e:
        print("Something wrong calling SoilGrids for soil data \n")
        print (e)
        sys.exit(1)

    #print ("\n")
    #print ("URL called: %s" % response.url)
    #print ("HTTP Staus Code: %s " % response.status_code)
    #print ("\n")
    
    return(response.json())


def apixuWeather(latitude,longitude,date):

    API_KEY = "cd058c7cdb4e4706b8f161546170602"
    domain = "api.apixu.com/v1"
    route = "history.json"          #Alternatives are "current" and "forecast", also as xml
    url = "http://%s/%s" % (domain,route)
    location = "%s,%s" % (latitude,longitude)
        
    payload = {"key" : API_KEY, "q" : location, "dt" : date}

    try:
        response = requests.get(url, params = payload)

    except requests.exceptions.ConnectionError as e:
        print("Something wrong calling APIXU for weather data \n")
        print (e)
        sys.exit(1)

    #print ("\n")
    #print ("URL called: %s" % response.url)
    #print ("HTTP Staus Code: %s " % response.status_code)
    #print ("\n")

    return(response.json())


def main():

    # Irish Hill, Kintbury
    latitude = "51.399205"
    longitude = "-1.424458"
 
    # Get soil data 
    SoilGridsResponse = retrieveSoilGridsData(latitude,longitude)    
    #pprint(SoilGridsResponse)

    # Parse out CEC at 0.1m (sl2)
    CEC_10 = SoilGridsResponse['properties']['CECSOL']['M']['sl2']
    units = SoilGridsResponse['properties']['CECSOL']['units_of_measure']
    print (" \n CEC at 0.1m: %s %s" % (CEC_10, units))


    # Get weather data    
    dayCount = 5
    dates = []
    now = datetime.now()
    
    while dayCount > 0:
        date = now - timedelta(dayCount)
        strDate = date.strftime("%Y-%m-%d")
        dates.append(strDate)
        dayCount = dayCount - 1

    totalPrecip = 0.0
    
    for date in dates:
        apixuResponse = apixuWeather(latitude, longitude, date)
        #pprint(apixuResponse)

        # Parse out total precipitation for the day
        # NB "forecastday" is a list so needs an index to resolve
        dayPrecip = apixuResponse['forecast']['forecastday'][0]["day"]['totalprecip_mm']
        responseDate = apixuResponse['forecast']['forecastday'][0]["date"]
        print (" \n Precipitation for %s: %.1f mm" % (responseDate, dayPrecip))
        totalPrecip = totalPrecip+dayPrecip

    print(" \n Total precipitation for the period was %.1f mm" % (totalPrecip))


if __name__ == "__main__":
    main()
    

