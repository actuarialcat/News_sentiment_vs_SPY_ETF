#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 11:26:26 2020

@author: jackson
"""

import pandas as pd 
from textblob import TextBlob


###################################################
# Global Param

OUTPUT_PATH = ""
OUTPUT_FILENAME_PREFIX = "web_data_"

STOCK_DATA_PATH = ""


###################################################
# Load data functions

def read_data_month(year, month):
    """read main data table file"""
    
    df = pd.read_csv(OUTPUT_PATH + OUTPUT_FILENAME_PREFIX + str(year) + str(month).zfill(2) + ".csv", index_col = 0)
    
    return df



def concat_text_data():
    """concat CSV file into single dataframe"""
    
    # Initialize dataframe
    df = pd.DataFrame()
    
    # Loop through all files
    #for year in range(2019, 2019 + 1):
    #    for month in range (1, 12 + 1):            
    #        df = df.append(read_data_month(year, month), ignore_index = True, sort=False)

    #last year
    year = 2020
    for month in range (9, 9 + 1):            
            df = df.append(read_data_month(year, month), ignore_index = True, sort=False)              

    return df



def read_stock_data():
    """load stock data"""
    
    df = pd.read_csv(STOCK_DATA_PATH, index_col = 0)
    
    return df



###################################################
# Data validation functons
    
def validate_record(row):
    """validate the record to ensure data is within expectation"""
    
    # timestamp within date
    if (str(row["date"]) == str(row["timestamp"])[0:8]):
        pass
    else:
        return False
    
    return True
    


def valid_df(df):
    """validate the whole dataframe"""
    
    valid_df = df.apply(validate_record, axis=1)
    
    return all(valid_df)



###################################################
# Data analytics functons
    





#%% ###################################################
# Main

df = concat_text_data()



#%% validate data
valid_df(df)














