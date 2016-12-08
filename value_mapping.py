import nlp_field_mapping as nfm
import os
import pandas as pd
import numpy as np
import string

# -- Replace below path with your correct directory structure
baseDir = "/Users/yisilala/Documents/IBM/projects/schlumberger oil company/"
inDir = os.path.join(baseDir, 'data')
outDir = os.path.join(baseDir, "mapping/output")

# -- In case preferred path does not already exist
if not os.path.exists(outDir):
    os.makedirs(outDir)


legacy_file = os.path.join(inDir, "legacy value.csv")
sap_file = os.path.join(inDir, "sap value.csv")
data_file = os.path.join(inDir, "mock data.csv")
field_mapping_file = os.path.join(outDir, "field_match_based_on_description.csv")


# -- Directory into which matched results spreadsheet is saved
outFile = os.path.join(outDir, "value mapping")
match_vals = nfm.fuzzyWordMatch(sap_file, legacy_file, 'DESCRIPTION', 'DESCRIPTION', 'VALUE', 'VALUE', outFile, 1)
# print(match_vals)

legacy_value = pd.read_csv(legacy_file, quotechar='"', skipinitialspace=True, sep=',')
match_vals.insert(0,'Column', legacy_value['COLUMN'])
match_vals.to_csv(str(outFile + ".csv"))

legacy_data = pd.read_csv(legacy_file, quotechar='"', skipinitialspace=True, sep=',')
legacy_data = pd.DataFrame(legacy_data)
col_to_check = legacy_data['COLUMN'].unique()
# print(col_to_check)


data_all = pd.read_csv(data_file, quotechar='"', skipinitialspace=True, sep=',')
data = pd.DataFrame(data_all)
# print(data)


mapping_sap = match_vals['Match1'].tolist()
mapping_legacy_lower = []
for item in match_vals['legacy_original']:
    # print('item is: ', item)
    mapping_legacy_lower.append(item.lower())
# print(mapping_legacy_lower)

for col in data.columns.values:
    if col not in col_to_check:
        continue

    ### so basically replace all the na values in the column so that there's a guarantee there'll be a mapping for that
    # repace the na values to 0 also allows me to say okay if the item is equal to 0 then just add smth else to it
    data[col] = data[col].fillna('0')
    row_to_replace = []

    for row in data[col]:
    # for i in range(0, len(data[col])):

        # here is where i implement if the value is equal to 0 then just replace it with "none"
        # if data[col][i] == "0":
        if row == "0":
            row_to_replace.append('none')

        else:
            ### so basically, 3 steps here:
            # 1. find maching value between the legacy value and the sap value,
            # 2. find the index in the sap value file
            # 3. replace the data[col] row with that value from the sap value file at that specific index
            match_index_in_mapping = mapping_legacy_lower.index(str(row).lower())
            # match_index_in_mapping = mapping_legacy_lower.index(str(data[col][i]).lower())
            row_to_replace.append(mapping_sap[match_index_in_mapping])
    data[col] = row_to_replace

data = data.fillna("")
# print(data)

### finally replace the field names with the output from your nlp algorithm
field_mapping = pd.read_csv(field_mapping_file, quotechar='"', skipinitialspace=True, sep=',')
# print(field_mapping)

data_col_names = data.columns.values.tolist()
# print(data_col_names)

new_col_names = []
# since field_mapping is a pandas dataframe, and field_mapping['legacy_original'] is pandas series
# you need to convert it to a list so then you can use the function "index()", which is pandas specific function
mapping_data = field_mapping['legacy_original'].tolist()

for col in data_col_names:
    match_index_in_mapping = mapping_data.index(col)
    new_col_names.append(field_mapping['Match1'][match_index_in_mapping])
print(new_col_names)

# replace the column names with new col names
data.columns = new_col_names

print(data)
writeFile = os.path.join(outDir, "value + field mapping")
data.to_csv(str(writeFile + ".csv"))