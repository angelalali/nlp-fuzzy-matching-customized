import difflib
import string

# -- DistrictNameMatching.py
# Author: Anthony Louis D'Agostino (ald2187 [at] columbia.edu)
# Purpose: Given CSV lists of district-state name pairs, identifies the best match given the fuzzywuzzy library
# Notes: Default number of matches currently set to 3, though can be modified as input argument.
# **** AUTHOR NOT LIABLE FOR ANY DAMAGES INCURRED THROUGH THE USE OR [ESPECIALLY] MISUSE OF THIS PRODUCT ***** </code>

import os
import numpy as np
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd


# a function that normalizes strings by stripping punctuations, whitespaces, and cnovert to lower cases
def normalize(s):
    for p in string.punctuation:
        # included in the punctuation: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
        s = s.replace(p, ' ')
    return s.lower()

def fuzzyWordMatch(tab1, tab1_name, tab2, tab2_name, tab1_des_col, tab2_des_col, tab1_field_col, tab2_field_col, outFile, num_match):
    """
    think of tab1 = tab2 table & tab2 = tab1 table IF AND WHEN you are trying to see which fields in tab1 matches w fields in tab2

    tab1: the tab1 metadata description
    tab2: the tab2 metadata description
    tab1_des_col: column name of the column in tab1 that contains the description of the tab1 field names
    tab2_des_col: column name of the column in tab2 that contains the description of the tab2 field names
    tab1_field_col: column name of the column in tab1 containing the tab1 field names
    tab2_field_col: column name of the column in tab2 containing the tab2 field names
    num_match: number of matches generated, default is 3
    outFile: includes path and filename for an outputted DTA file - should be "*.dta"
    """

    print('... mapping '+tab1_name+" to "+tab2_name)

    # tab1 = pd.read_csv(tab1, quotechar='"', skipinitialspace=True, sep=',')
    # # print(" *** Now printing column values for tab1 file *** ")
    # # print(list(tab1.columns.values))
    #
    # tab2 = pd.read_csv(tab2, quotechar='"', skipinitialspace=True, sep=',')
    # # print(" *** Now printing column values for tab2 file *** ")
    # # print(list(tab2.columns.values))

    # store the texts in a diff obj
    tab1_text = tab1[tab1_des_col]
    tab1_fields = tab1[tab1_field_col]
    tab2_text = tab2[tab2_des_col]

    # normalize both tab1 & tab2 text objects
    tab1_text_normalized = []
    for text in tab1_text:
        tab1_text_normalized.append(normalize(str(text)))

    tab2_text_normalized = []
    for text in tab2_text:
        tab2_text_normalized.append(normalize(str(text)))

    # create top 3 match list using FuzzyWuzzy's built in process.extract() function, which default produce top 5 matches
    top3_matche_list = [process.extract(x, tab1_text_normalized, limit=num_match) for x in tab2_text_normalized]
    # so the output is a tuple of 3 values!
    # fhp_new[x][y][z]
    # x = [0-nrow(top3_matche_list)]; row number; basically which tab2 word you are trying to match
    # y = [0-2]; which match; there are 3 for each word;
    # z = [0,1]; every match has two values: (match word, score btwn 0-100)

    # -- generate column names for the new table "match_info"
    lab = tab2_name+"_original"
    lab_index = ""
    lab_score = ""
    i = 1
    # while i <= num_match:
    #     lab = lab + " " + "Match" + str(i)
    #     lab_index = lab_index + " " + "Index" + str(i)
    #     lab_score = lab_score + " " + "Score" + str(i)
    #     i += 1
    while i <= num_match:
        lab = lab + " " + tab1_name+"_Match" + str(i)
        # lab = lab + " " + "Index" + str(i)
        lab = lab + " " + tab1_name+"_Description" + str(i)
        lab = lab + " " + "Score" + str(i)
        i += 1


    # so im going to create a giant table with all the matching info in it, such as the matching word and its score
    match_info = pd.DataFrame(columns=lab.split())

    for i in range(0,num_match):
        # so we create empty arrays that we can then append values to it
        word_match = []
        # index_match = []
        descri_match = []
        score_match = []
        for row in top3_matche_list:
            index_to_add = tab1_text_normalized.index(row[i][0])
            word_match.append(tab1_fields.iloc[index_to_add])
            # index_match.append(index_to_add)
            descri_match.append(tab1[tab1_des_col].iloc[index_to_add])
            score_match.append(row[i][1])
        j = i+1
        match_info[tab1_name+'_Match{}'.format(j)] = word_match
        # match_info['Index{}'.format(j)] = index_match
        match_info[tab1_name+'_Description{}'.format(j)] = descri_match
        match_info['Score{}'.format(j)] = score_match

    ## this dataframe d will be storing ALL your results, w first column being the original tab2 column to match
    d = pd.DataFrame(columns=lab.split())
    d[tab2_name+'_original'] = tab2[tab2_field_col]
    # d['tab2_description'] = tab2[tab2_des_col]

    # d['tab2_original'] = tab2[tab2_des_col]
    # basically fill in all the columns in df d with matching column names in df match_info
    for x in range(1, num_match + 1):
        d[tab1_name+"_Match{}".format(x)] = [y for y in match_info[tab1_name+'_Match' + str(x)]]
        # d["Index{}".format(x)] = [y for y in match_info['Index' + str(x)]]
        d[tab1_name+"_Description{}".format(x)] = [y for y in match_info[tab1_name+'_Description' + str(x)]]
        d["Score{}".format(x)] = [y for y in match_info['Score' + str(x)]]

    ### dont think the'll ever be perfect match or whether this info is usefl... so i dont think i need it
    # d['perfect_match'] = d['Match1'] == d['tab2_original']

    ### insert tab2 data column description since they requested it
    # using idx = 0 will insert at the beginning
    # df.insert(idx, col_name, value)
    d.insert(1,tab2_name+'_description', tab2[tab2_des_col])

    out = pd.DataFrame(d)
    # out.to_stata(str(outFile + ".dta"))
    out.to_excel(str(outFile + ".xlsx"))
    # print("******************************************")
    # print("*** Your analysis has been completed! *** ")
    # print("******************************************")

    return out


