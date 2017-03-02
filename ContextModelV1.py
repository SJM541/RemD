
# ContextModelV1


import sys
import requests
from pprint import pprint
from datetime import datetime, timedelta
import pandas as pd


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

    return(response.json())


def soilData(latitude,longitude):
    
    # Get soil data
    # Return just CEC at 0.1m for now
    # 
    # - will extend to return a DataFrame of all required soil data whan known

    SoilGridsResponse = retrieveSoilGridsData(latitude,longitude)    
    #pprint(SoilGridsResponse)

    # Parse out CEC at 0.1m (sl2)
    CEC_10 = SoilGridsResponse['properties']['CECSOL']['M']['sl2']
    CEC_units = SoilGridsResponse['properties']['CECSOL']['units_of_measure']
    # print (" \n CEC at 0.1m: %s %s" % (CEC_10, CEC_units))
    return CEC_10
    


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

    return(response.json())



def weatherData(latitude,longitude,numDays):

    # Get weather data for today and previous <numDays> days
    # For now, returns just total precipitation
    # - will extebnd to return DataFrame with temp etc.

    dayCount = numDays
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
        # print (" \n Precipitation for %s: %.1f mm" % (responseDate, dayPrecip))
        totalPrecip = totalPrecip+dayPrecip

    return totalPrecip



def countryAndCropFilter(targetCountry,targetCrop,fileName):

    locations = pd.read_excel(open(fileName,'rb'),sheetname='CPC_pest_location_model_data')
    crops = pd.read_excel(open(fileName,'rb'),sheetname='CPC_crop-host_model_data')

    # Create list of pests in the chosen country
    countrySelectionList=[]  
    for index, row in locations.iterrows():              # Iterrows is a Genrator from Pandas
        if row['Country'] == targetCountry:
            countrySelectionList.append(row['Scientific name'])
    countrySelection = pd.DataFrame(countrySelectionList, columns=['Scientific name'])    
    print('countrySelection\n')
    print(countrySelection)

 
    # Create list of pests of the chosen crop and then place in a DataFrame
    rowList=[]
    for index, row in crops.iterrows():             
        if row['Crop'] == targetCrop:
            rowList.append([row['Scientific name'],row['Host Type']])
    cropSelection = pd.DataFrame(rowList, columns=['Scientific name','Host Type'])
    print('\n cropSelection \n')
    print(cropSelection)

    
    # Innner join on cropSelection and countrySelection
    pestsOfCropInCountry = pd.merge(cropSelection,countrySelection,on='Scientific name',how='inner')
    
    return pestsOfCropInCountry


def environmentalMultipliers(pests,crop,fileName):

    # Takes DataFrame of pests and location of lookup data
    # Returns a DataFrame of pests and their environmental multipliers

    # NB Game_model_data table contains multiple entries for each pest organism
    # because it is organised by crop and a pest may be of >1 crop
    
    multipliers = pd.read_excel(open(fileName,'rb'),sheetname='Game_model_data')

    # Inner join of pests and multipliers
    # This gives multipliers for pests of crop, in country, but with multiple entries
    # - see "NB" above
    envMultipliers = pd.merge(pests,multipliers, on='Scientific name', how='inner')

    # Filter again for crop
    envCropMultipliers = envMultipliers[(envMultipliers.Crop==crop)]
    
    return envCropMultipliers



def main():

    # Setup
    latitude = "51.399205"      # Irish Hill, Kintbury
    longitude = "-1.424458"
    weatherDays = 5             # Number of days over which to accumulate historical weather data
    #targetCountry='UK'
    #targetCrop = 'Cabbage'
    targetCountry='Kenya'
    targetCrop = 'Maize'
    parametersFile = 'C:/Users/marshalls/Documents/SJM/RemoteDiagnostics/ContextModel/Remote_Diagnostics_Data.xlsx'
    
    # Get Soil Data
    #CEC = soilData(latitude,longitude)
    #print(' CEC at 10cm: %s \n' % CEC)
    
    # Get WeatherData
    #totalPrecip = weatherData(latitude,longitude,weatherDays)    
    #print("\n Total precipitation for the period was %.1f mm" % (totalPrecip))

    cropCountryPests = countryAndCropFilter(targetCountry, targetCrop, parametersFile)
    print('\n Pests of %s in county %s \n' % (targetCrop, targetCountry))
    print(cropCountryPests)

    # get the environmental multipliers for the pests of the ctop in the country
    multipliers = environmentalMultipliers(cropCountryPests,targetCrop,parametersFile)
    print('Multipliers in filtered list \n')
    print(multipliers)


if __name__ == "__main__":
    main()
    

