import nlp_field_mapping as nfm
import os
import pandas as pd
import numpy as np

from collections import Counter
# allows you to count frequency of ALL elements in a list
import re
# allows you to use regex
import openpyxl
# so you can use pandas' to_excel()


"""
BASIC FILES/PATHS WHOSE USE IS REPEATED
"""

# -- Replace below path with your correct directory structure
baseDir = "/Users/yisilala/Documents/IBM/projects/schlumberger oil company/data input & output/real data/"
inDir = os.path.join(baseDir, 'input/MATERIAL VALUE')
outDir = os.path.join(baseDir, "output/MATERIAL VALUE")

# -- In case preferred path does not already exist
if not os.path.exists(outDir):
    os.makedirs(outDir)

"""
read and prepare the files
"""
### read the legacy file data
legacy_file = os.path.join(inDir, "Oracle_MI_UOM_only_english.xlsx")

# read ALL the tabs in the legacy file; there are 5 in total but we don't care about the 5th one, which is phone tab
col_names=["UOM_CODE","DESCRIPTION"]
legacy_data_all = pd.read_excel(legacy_file, sheetname=0, header=0, na_values="", names=col_names)
# print(legacy_data_all.iloc[:45,:])

# clean the legacy table; lots of rows contain descriptions in russian or other languages; what good do they bring?
# clear them out before you apply matching; so basically you want to remove non-ASCII characters
for i in range(0, len(legacy_data_all["DESCRIPTION"])):
    legacy_data_all["DESCRIPTION"][i] = re.sub(r'[^\x00-\x7F]+','nonascii ', legacy_data_all["DESCRIPTION"][i])

# now filter out all the rows that have been labeled w "nonascii" that yo've put in for nonascii symbols in previous line
legacy_data_clean = legacy_data_all[legacy_data_all.DESCRIPTION.str.contains("nonascii")==False]
# print(legacy_data_clean.iloc[:45, :])

# also you dont want rows w repeating descriptions,
# you definitely dont want those noise rows there to confuse your matching;
# so basically what i'm doing here is to see if any comments are repeated multiple times (right now, i think twice is okay)
# if it's repeated, then i will take them out
c = Counter(legacy_data_clean['DESCRIPTION'])
unique_comments = []

for val in set(legacy_data_clean.DESCRIPTION):
    if c[val] < 3:
        unique_comments.append(val)
# print(unique_comments)

# lets check if all comments are unique
# print(len(set(unique_comments))/len(legacy_data_clean))
# which came to about .972, so okay, mostly not duplicated.

# but we'll still get rid of the duplicates.
legacy_data = legacy_data_clean.ix[legacy_data_clean.DESCRIPTION.isin(unique_comments),:]
legacy_data.reset_index(range(0, len(legacy_data)), inplace=True)
# print(legacy_data)


### read all sap files
sap_file = os.path.join(inDir,"SAP_VALUES_UOM.xlsx")
sap_data_all = pd.read_excel(sap_file, sheetname=0, header=0)
# print(sap_data.columns.values)
# print(sap_data_all.iloc[:15, :])
# can use above line to check first 15 rows of your combined sap data


## next lets find out what's the unique value to all Measurement unit text (sap description) rate in SAP file
# print(len(set(sap_data_all['Measurement unit description']))/len(sap_data_all))
# = .9935
# so this means that there's only 1 or 2 repeats. so let's just drop the repeats real quick

# method 1: use pandas built in drop_duplicates()
sap_data_clean = sap_data_all.drop_duplicates(['Measurement unit description'])

# method 2: use sort_index()
# sap_data_clean = sap_data_all.sort_index().groupby('ISO code').filter(lambda group: len(group) == 1)

# there are also some empty cells in the 'ISO code' column, so drop those rows as well
# basically get the rows where ISO code is NOT null
sap_data = sap_data_clean.dropna(subset=['ISO code'])

# reset index values of the sap_file (otherwise you'll get many rows w same row index numbers!)
sap_data.reset_index(range(0,len(sap_data),1), inplace=True)
# print(sap_data['ISO code'])


# ### read the transformation file to collect the sap columns that actually matters
# needed_sap_col_file = os.path.join(inDir,'MATERIAL/sap needed.xlsx')
# needed_sap_col_data = pd.read_excel(needed_sap_col_file, sheetname='Field List - All Views', header=0, skiprows=0, na_values="")
# # when you read excel using pandas read_excel function, the result is ALREADY in pandas dataframe type
#

# ### now see which sap fields in the sap_data are also in needed_sap_col, and you'll only keep those
# # first, need to extract the field names (in the file, the field name is in format: TableName.FieldName
# # so need to strip anything before the "."
# temp = needed_sap_col_data.ix[needed_sap_col_data['R2 Field Conversion'] == 'INSCOPE','Table.Field']
# needed_sap_cols = [re.sub("^[a-zA-Z]*.", "", x) for x in temp]
# # print(needed_sap_cols)
# sap_fields = sap_data.ix[sap_data['Field'].isin(set(needed_sap_cols)),:]
# sap_fields = sap_fields.reset_index(range(0,len(sap_fields)))
# # print(sap_fields)




### using legacy's comment to match
# """
# # call the matching function
# # """
# -- Directory into which matched results spreadsheet is saved
outFile = os.path.join(outDir, "sap to legacy mapping")
match_vals = nfm.fuzzyWordMatch(sap_data_clean, 'sap', legacy_data, 'legacy', 'Measurement unit description',
                                'DESCRIPTION', 'ISO code', 'UOM_CODE', outFile, 3)

### now add the answer to the output
answer_file = os.path.join(inDir, "value_table_uom(Legacy_To_SAP_Mapping).xlsx")
answer_table = pd.read_excel(answer_file, sheetname=0, header=0)
answer_table = answer_table[['LEGACY_VALUE', "ECCISOUOM"]]
print(answer_table)

# merge the above table w the answer table produced by the fuzzy matching fxn
output_all = pd.merge(answer_table, match_vals, how='right', left_on='LEGACY_VALUE', right_on='legacy_original')
print(output_all)
output_all.to_excel(str(outFile + ".xlsx"))

# outFile = os.path.join(outDir, "legacy to sap field mapping.xlsx")
# match_vals = nfm.fuzzyWordMatch(legacy_data, 'legacy', sap_data_clean, 'sap', 'DESCRIPTION',
#                                 'Measurement unit description', 'UOM_CODE', 'ISO code', outFile, 3)



# ### using legacy's field name to match (ignore its comments)
# """
# # call the matching function
# # """
# # -- Directory into which matched results spreadsheet is saved
# outFile = os.path.join(outDir, "sap to legacy mapping")
# match_vals = nfm.fuzzyWordMatch(sap_fields, 'sap', legacy_data_clean, 'legacy', 'Description', 'Name', 'Field', 'Name', outFile, 3)
#
#
# outFile = os.path.join(outDir, "legacy to sap field mapping")
# match_vals = nfm.fuzzyWordMatch(legacy_data_clean, 'legacy', sap_fields, 'sap', 'Name', 'Description', 'Name', 'Field', outFile, 3)