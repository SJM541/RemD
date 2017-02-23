
# Tryout for reading pest-crop data from excel file


import pandas as pd


def main():


    countryName='UK'
    cropName = 'Cabbage'

    print ('working')

    fileName = 'C:/Users/marshalls/Documents/SJM/RemoteDiagnostics/ContextModel/Remote_Diagnostics_Data.xlsx'

    Locations = pd.read_excel(open(fileName,'rb'),sheetname='CPC_pest_location_model_data')
    Hosts = pd.read_excel(open(fileName,'rb'),sheetname='CPC_crop-host_model_data')

    print('Locations \n')
    print(Locations)
    print('\n Hosts \n')
    print(Hosts)

    countrySelection=[]
    
    
    for loc in Locations['Country']:
        print(loc)
        if (loc == countryName):
            countrySelection.append(Locations['Scientific name']) # Hasn't appended anything!
    print(countrySelection)

    # do same for crops
    # merge the countrySelection and cropSelection dfs based on common scientific names
    
    
    
if __name__ == "__main__":
    main()
