#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 11:26:26 2020

@author: jackson
"""

import pandas as pd 
from textblob import TextBlob

from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics

###################################################
# Global Param

OUTPUT_PATH = "web_data/"
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
# Data validation functions
    
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
# Text analytics functions
    
def text_sentiment(inp):
    """Extract sentiment score from text"""
    
    str_inp = str(inp)
    s = TextBlob(str_inp).sentiment
    
    s_pol = s.polarity      # How positive the text is.
    s_sub = s.subjectivity  # How subjective the text is.
        
    return s_pol, s_sub, str_inp



def make_sentiment_features(df):
    """Make a dataframe including text sentiment features"""
    
    df_time = df.iloc[:, 0:1]
    df_sen = df.iloc[:, 2:22].applymap(text_sentiment)

    df_pol = df_sen.applymap(lambda x: x[0])
    df_sub = df_sen.applymap(lambda x: x[1])
    
    df_feature = pd.concat([df_pol.add_suffix('_pol'), df_sub.add_suffix('_sub')], axis=1, sort=False)
    df_feature = pd.concat([df_time, df_feature], axis=1, sort=False)

    return df_feature



###################################################
# Machine learning functions

def ml_random_forest(df):
    """Random forest model"""
    
    # Define train / test data set
    x_train = df.iloc[:, 1:41]         # Features
    x_test = 0
    
    y_train = df.iloc[:, 41:42]         # Labels
    y_test = 0
    
    
    # Define model parameters
    rf = RandomForestClassifier(
            n_estimators = 100      # number of trees
        )
    
    # Train model
    rf.fit(x_train, y_train)

    # Predict on test set
    y_pred = rf.predict(x_test)

    print("Accuracy:", metrics.accuracy_score(y_test, y_pred))

    return rf




#%% ###################################################
# Main

#Load data
df = concat_text_data()


#%% validate data

valid_df(df)


#%% text analytics

df_feature = make_sentiment_features(df)


#%% text analytics












