
# Tryout for reading pest-crop data from excel file


import pandas as pd


def main():

    targetCountry='UK'
    targetCrop = 'Cabbage'

    fileName = 'C:/Users/marshalls/Documents/SJM/RemoteDiagnostics/ContextModel/Remote_Diagnostics_Data.xlsx'

    locations = pd.read_excel(open(fileName,'rb'),sheetname='CPC_pest_location_model_data')
    crops = pd.read_excel(open(fileName,'rb'),sheetname='CPC_crop-host_model_data')

   # Create list of pests in the chosen country
    countrySelection=[]  
    for index, row in locations.iterrows():              # Iterrows is a Genrator from Pandas
        if row['Country'] == targetCountry:
            countrySelection.append(row['Scientific name'])
    print('countrySelection\n')
    print(countrySelection)


    # Create list of pests of the chosen crop and then place in a DataFrame
    rowList=[]
    for index, row in crops.iterrows():             
        if row['Crop'] == targetCrop:
            rowList.append([row['Scientific'],row['Host Type']])
    cropSelection = pd.DataFrame(rowList, columns=['Scientific name','Host Type'])
    print('\n cropSelection \n')
    print(cropSelection)


    # get the intersection of the countrySelection and cropSelection based on scientific names
    pestList=[]
    for pest in countrySelection: 
        for index, row in cropSelection.iterrows():
            if pest == row['Scientific name']:
                pestList.append([row['Scientific name'],row['Host Type']])
    pestsOfCropInCountry = pd.DataFrame(pestList, columns=['Scientific name','Host Type'])
    print('Pests of %s in county %s \n' % (targetCrop, targetCountry))
    print(pestsOfCropInCountry)


if __name__ == "__main__":
    main()
