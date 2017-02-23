
# Tryout for reading pest-crop data from excel file


import pandas as pd

df = pd.read_excel(open('C:/Users/marshalls/Documents/SJM/RemoteDiagnostics/ContextModel/Remote_Diagnostics_Data.xlsx','rb'),sheetname='CPC_crop-host_model_data')
