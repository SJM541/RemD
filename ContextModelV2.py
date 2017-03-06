
# ContextModelV2


# TO DO

#   Presence or absesnce in country acts as hard filter but would like to
#   apply a factor instead of exclude.

#   Does not take any account of Major or Minor pest staus - just is or is not
#   a pest of the crop. Add in this factor.

#   Tidy up naming - some are clumsey

#   Currently only uses preciptation data to set score
#   Add in temperature and wind


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
    # - will extend to return a DataFrame of all required soil data when known

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
    # For now, returns total precipitation and wet days, as a Dictionary

    dayCount = numDays
    dates = []
    now = datetime.now()
    
    while dayCount > 0:
        date = now - timedelta(dayCount)
        strDate = date.strftime("%Y-%m-%d")
        dates.append(strDate)
        dayCount = dayCount - 1

    totalPrecip = 0.0
    wetDays = 0
    
    for date in dates:
        apixuResponse = apixuWeather(latitude, longitude, date)
        #pprint(apixuResponse)

        # Parse out total precipitation for the day
        # NB "forecastday" is a list so needs an index to resolve
        dayPrecip = apixuResponse['forecast']['forecastday'][0]["day"]['totalprecip_mm']
        responseDate = apixuResponse['forecast']['forecastday'][0]["date"]
        #print (" \n Precipitation for %s: %.1f mm" % (responseDate, dayPrecip))
        if dayPrecip > 0.0:
            wetDays = wetDays+1
        totalPrecip = totalPrecip+dayPrecip
        
    # Force "Dry"
    #wetDays = 0
    #totalPrecip = 0.1

    # Force "Wet"
    #wetDays = 10
    #totalPrecip = 50.0
    
    weatherSummary = {'wetDays':wetDays, 'totalPrecip':totalPrecip}
    #print(weatherSummary)

    return weatherSummary


def assessWeather(summaryData):

    # Takes summary weather data (for now just totalPrecip and wetDays)
    # and returns assessment of wet, dry, hot and windy
    # as a Dictionary of Boolean values

    # These thresholds need careful consideration!
    
    wetPrecipThreshold = 1.0        # "Wet" if more than n mm rain    
    wetDaysThreshold = 5            #   and more than n wet days
    dryPrecipThreshold = 0.5        # "Dry" if less than n mm rain
    dryDaysThreshold = 0            #   and less than n wet days 

    isWet = False
    isDry = False
    isHot = False
    isWindy = False

    if (summaryData['totalPrecip'] > wetPrecipThreshold)and(summaryData['wetDays'] > wetDaysThreshold):
       isWet = True
    if (summaryData['totalPrecip'] < dryPrecipThreshold)and(summaryData['wetDays'] <= dryDaysThreshold):
       isDry = True

    return ({'wet': isWet, 'dry': isDry, 'hot': isHot, 'windy': isWindy})



def scoreForCountry(locations,targetCountry):


    inCountryScore = 1.5
    notInCountryScore = 0.5

    scoredPests = locations
    
    # Create list of pests in the chosen country
    countryScoreList=[]  
    for index, row in scoredPests.iterrows():              # Iterrows is a Generator from Pandas
        if row['Country'] == targetCountry:
            countryScoreList.append(inCountryScore)
        else:
            countryScoreList.append(notInCountryScore)
    scoredPests['Country Score'] = countryScoreList
    #print(scoredPests)
    return scoredPests


def scoreForCrop(pests,crops,targetCrop):
    
    majorCropScore = 1.5
    minorCropScore = 1.2
    notOnCropScore = 0.5
    
    cropScoreDict={}
    for index, row in crops.iterrows():             
        if row['Crop'] == targetCrop:
            if(row['Host Type'] == 'Major'):
                cropScoreDict[row['Scientific name']] = majorCropScore
            elif(row['Host Type'] == 'Minor'):
                cropScoreDict[row['Scientific name']] = minorCropScore
        else:
            cropScoreDict[row['Scientific name']] = notOnCropScore

    print(cropScoreDict)

    #cropScoreDF = pd.DataFrame.from_dict(data=cropScoreDict,orient='index')
    #Below is more clumsey but provides column headings to use later in the merge
    cropScoreDF = pd.DataFrame()
    cropScoreDF['Scientific name'] = cropScoreDict.keys()
    cropScoreDF['Crop Score'] = cropScoreDict.values()
    print('\n crop score DF \n')
    print(cropScoreDF)

    # Innner join on cropSelection and countrySelection
    cropAndCountryScores = pd.merge(cropScoreDF,pests,on='Scientific name',how='inner')
    
    return cropAndCountryScores


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
    envCropMultipliers = envMultipliers[(envMultipliers.Crop == crop)]
    
    return envCropMultipliers


def applyModelFactors(multipliers, weather):

    # Takes a DataFrame of pests with model scores and a Dict of weather attributes
    # Returns DataFrame of pest species and overall scores

    isWet = weather['wet']
    isDry = weather['dry']
    isHot = weather['hot']
    isWindy = weather['windy']

    #isWet = False
    #isDry = True
    #isHot = True
    #isWindy = True

    scoreDict = {}
    for index, row in multipliers.iterrows():
        score = 1.0
        if isWet:
            score = score * row['Mwet']
        if isDry:
            score = score * row['Mdry']
        if isHot:
            score = score * row['Mhot']
        if isWindy:
            score = score * row['Mwind']           
        scoreDict[row['Scientific name']] = score
    #print(scoreDict)
    pestScores = pd.DataFrame.from_dict(data=scoreDict,orient='index')

    return pestScores
        

def main():

    # Setup
    latitude = "-0.453718"      # Nyeri, Kenya
    longitude = "36.951524"
    weatherDays = 10            # Number of days over which to accumulate historical weather data
    targetCountry='Kenya'
    targetCrop = 'Cabbage'
    parametersFileName = 'C:/Users/marshalls/Documents/SJM/RemoteDiagnostics/ContextModel/Remote_Diagnostics_Data.xlsx'
    
    # Get Soil Data
    #CEC = soilData(latitude,longitude)
    #print(' CEC at 10cm: %s \n' % CEC)
    
    # Get WeatherData
    #weatherSummary = weatherData(latitude,longitude,weatherDays)    
    #print("\n Total precipitation for the period was %.1f mm" % (weatherSummary['totalPrecip']))
    #print(" Number of wet days was %d" % (weatherSummary['wetDays']))

    #weatherFactors = assessWeather(weatherSummary)
    #print(weatherFactors)
    
    # DataFrames to hold location and crop data
    locations = pd.read_excel(open(parametersFileName,'rb'),sheetname='CPC_pest_location_model_data')
    crops = pd.read_excel(open(parametersFileName,'rb'),sheetname='CPC_crop-host_model_data')


    countryScoredPests = scoreForCountry(locations,targetCountry)
    #print(countryScoredPests)

    countryCropScoredPests = scoreForCrop(countryScoredPests,crops,targetCrop)
    print(countryCropScoredPests)


    # get the environmental multipliers for the pests of the crop in the country
    #multipliers = environmentalMultipliers(cropCountryPests,targetCrop,parametersFile)
    #print('Multipliers in filtered list \n')
    #print(multipliers)

    # Apply factors for weather to generate a scored set of pest species
    #scoredPests = applyModelFactors(multipliers, weatherFactors)
    #print('Pests of the crop, in the country, scored for impact of weather \n')
    #print(scoredPests)


if __name__ == "__main__":
    main()
    

