import nlp_field_mapping as nfm
import os
import pandas as pd

from collections import Counter
# allows you to count frequency of ALL elements in a list
import re
# allows you to use regex


"""
BASIC FILES/PATHS WHOSE USE IS REPEATED
"""

# -- Replace below path with your correct directory structure
baseDir = "/Users/yisilala/Documents/IBM/projects/schlumberger oil company/data input & output/real data/"
inDir = os.path.join(baseDir, 'input')
outDir = os.path.join(baseDir, "output/MATERIAL")

# -- In case preferred path does not already exist
if not os.path.exists(outDir):
    os.makedirs(outDir)

"""
read and prepare the files
"""
### read the legacy file data
legacy_file = os.path.join(inDir, "MATERIAL/legacy data.xlsx")

# read ALL the tabs in the legacy file; there are 5 in total but we don't care about the 5th one, which is phone tab
col_names=["Name", "Datatype", "Length", "Mandatory", "Comments"]
legacy_data = pd.read_excel(legacy_file, sheetname='MTL_SYSTEM_ITEMS_B', header=0, na_values="", names=col_names)

### below code is used to read multiple legacy data sheets in one legacy excel file
# legacy_data = pd.DataFrame(columns=col_names)
# for i in range(0,6):
#     temp_dt = pd.read_excel(legacy_file, sheetname=i, header=0, na_values="", names=col_names)
#     legacy_data = legacy_data.append(temp_dt)
# legacy_data.reset_index(range(0, len(legacy_data)))
# print(legacy_data.iloc[:45,:])

# you want to clean the legacy file, since many rows are not used anymore;
# you definitely dont want those noise rows there to confuse your matching;
# so basically what i'm doing here is to see if any comments are repeated multiple times (right now, i think twice is okay)
# if it's repeated, then i will take them out
c = Counter(legacy_data['Comments'])
unique_comments = []

for val in set(legacy_data['Comments']):
    if c[val] < 3:
        unique_comments.append(val)
# print(unique_comments)

legacy_data_clean = legacy_data.ix[legacy_data['Comments'].isin(unique_comments),:]
# print(legacy_data_clean)


### read the sap files
sap_file = os.path.join(inDir, 'MATERIAL SAP/DataMARC.xlsx')
col_names = ["Field","Data_Type","Length","Description"]
sap_data = pd.read_excel(sap_file, sheetname=0, header=0)
# print(sap_data)
# sap_data = pd.DataFrame()


# print(sap_data.iloc[:15, :])
# can use above line to check first 15 rows of your combined sap data

# reset index values of the sap_file (otherwise you'll get many rows w same row index numbers!)
sap_data.reset_index(range(0,len(sap_data),1))
# print(sap_data.iloc[130:140, :])


### read the transformation file to collect the sap columns that actually matters
needed_sap_col_file = os.path.join(inDir,'MATERIAL/sap needed.xlsx')
# needed_sap_col_data = pd.read_excel(needed_sap_col_file, sheetname='Field List - All Views', header=0, skiprows=0, na_values="")
needed_sap_col_data = pd.read_excel(needed_sap_col_file, sheetname='ORACLE-MI', header=0, skiprows=0, na_values="")
# when you read excel using pandas read_excel function, the result is ALREADY in pandas dataframe type


### now see which sap fields in the sap_data are also in needed_sap_col, and you'll only keep those
# first, need to extract the field names (in the file, the field name is in format: TableName.FieldName
# so need to strip anything before the "."
temp = needed_sap_col_data.ix[needed_sap_col_data['R2 Field Conversion'] == 'INSCOPE','Table.Field']
needed_sap_cols = [re.sub("^[a-zA-Z]*.", "", x) for x in temp]
# print(needed_sap_cols)
sap_fields = sap_data.ix[sap_data['Field'].isin(set(needed_sap_cols)),:]
sap_fields = sap_fields.reset_index(range(0,len(sap_fields)))
# print(sap_fields)


## using legacy's comment to match
# """
# # call the matching function
# # """
# # # -- Directory into which matched results spreadsheet is saved
# # outFile = os.path.join(outDir, "sap to legacy mapping")
# # match_vals = nfm.fuzzyWordMatch(sap_fields, 'sap', legacy_data_clean, 'legacy', 'Description', 'Comments', 'Field', 'Name', outFile, 3)
#
#
# outFile = os.path.join(outDir, "legacy to sap field mapping")
# match_vals = nfm.fuzzyWordMatch(legacy_data_clean, 'legacy', sap_fields, 'sap', 'Comments', 'Description', 'Name', 'Field', outFile, 6)
#

### using legacy's field name to match (ignore its comments)
"""
# call the matching function
# """
# # -- Directory into which matched results spreadsheet is saved
# outFile = os.path.join(outDir, "sap to legacy mapping.xlsx")
# match_vals = nfm.fuzzyWordMatch(sap_fields, 'sap', legacy_data_clean, 'legacy', 'Description', 'Name', 'Field', 'Name', outFile, 3)


outFile = os.path.join(outDir, "legacy to sap field mapping.xlsx")
match_vals = nfm.fuzzyWordMatch(legacy_data_clean, 'legacy', sap_fields, 'sap', 'Name', 'Description', 'Name', 'Field', outFile, 3)