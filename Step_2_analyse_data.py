#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data pre-processing and fitting random forest models

Created on Thu Oct 22 11:26:26 2020

@author: Jackson
"""

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt

from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn import metrics

import datetime


###################################################
# Global Param

OUTPUT_PATH = "web_data/"
OUTPUT_FILENAME_PREFIX = "web_data_"

STOCK_DATA_PATH = "SPY.csv"


###################################################
# Load data functions

def read_data_month(year, month):
    """read main data table file"""
    
    df = pd.read_csv(OUTPUT_PATH + OUTPUT_FILENAME_PREFIX + str(year) + str(month).zfill(2) + ".csv", index_col = 0)
    
    return df



def concat_text_data():
    """concat CSV file into single dataframe"""
    
    # Parameters
    st_year = 2018
    st_month = 10
    en_year = 2020
    en_month = 9
    
    # Initialize dataframe
    df = pd.DataFrame()
    
    # first year
    for month in range (st_month, 12 + 1):            
            df = df.append(read_data_month(st_year, month), ignore_index = True, sort=False)      
    
    # Loop through all files
    for year in range (st_year + 1, en_year):
        for month in range (1, 12 + 1):            
            df = df.append(read_data_month(year, month), ignore_index = True, sort=False)

    # last year
    for month in range (1, en_month + 1):            
            df = df.append(read_data_month(en_year, month), ignore_index = True, sort=False)   
            
    return df



def read_stock_data():
    """load stock data"""
    
    df = pd.read_csv(STOCK_DATA_PATH, index_col = False)
    
    # Change date format and col name
    df.rename({'Date': 'date'}, axis=1, inplace=True)
    df["date"] = df["date"].apply(string_to_date_SPY)
    
    return df



def change_text_date_format(df):
    "Change text date format"
    
    df["date"] = df["date"].apply(string_to_date_text)
    
    

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
    


def validate_text_data(df):
    """validate the whole text dataframe"""
    
    valid_df_index = df.apply(validate_record, axis=1)
    valid_df = df[valid_df_index]
    
    print(str(len(df) - len(valid_df)) + " rows of invalid data removed")
    
    return valid_df



###################################################
# Data pre-processing functions
    
def string_to_date_SPY(inp):
    """Convert date format for stock data"""
    return datetime.datetime.strptime(inp, "%Y-%m-%d")

def string_to_date_text(inp):
    """Convert date format for text data"""
    return datetime.datetime.strptime(str(inp), "%Y%m%d")



###################################################
# Stock data pre-processing functions

def pre_process_stock_data(df_spy):
    
    # lag values
    df_spy["volume_next_1"] = df_spy["Volume"].shift(periods = -1)
    df_spy["adj_close_next_1"] = df_spy["Adj Close"].shift(periods = -1)
    
    # calcuate returns
    df_spy["ret_next_1"] = (df_spy["adj_close_next_1"] / df_spy["Adj Close"]) - 1
    df_spy["direction_up_next_1"] = df_spy["ret_next_1"].apply(lambda x: x > 0)
    
    # calcuate volume
    volume_cutoff = 75000000
    df_spy["volume_large_next_1"] = df_spy["volume_next_1"].apply(lambda x: x > volume_cutoff)



###################################################
# Text analytics functions
    
def text_sentiment_textblob(inp):
    """Extract sentiment score from text using TextBlob"""
    
    str_inp = str(inp)
    s = TextBlob(str_inp).sentiment
    
    s_pol = s.polarity      # How positive the text is.
    s_sub = s.subjectivity  # How subjective the text is.
        
    return s_pol, s_sub, str_inp



def make_sentiment_features_textblob(df):
    """Make a dataframe including text sentiment features using TextBlob"""
    
    df_time = df.iloc[:, 0:1]
    df_sen = df.iloc[:, 2:22].applymap(text_sentiment_textblob)

    df_pol = df_sen.applymap(lambda x: x[0])
    df_sub = df_sen.applymap(lambda x: x[1])
    
    # Concat to single data frame
    df_feature = pd.concat([df_pol.add_suffix('_pol'), df_sub.add_suffix('_sub')], axis=1, sort=False)
    df_feature = pd.concat([df_time, df_feature], axis=1, sort=False)

    return df_feature



def text_sentiment_NLTK(inp, sid):
    """Extract sentiment score from text using NLTK Vader"""
    
    if (isinstance(inp, str)):
        x = sid.polarity_scores(inp)
        return x["compound"]
    
    else:
        return 0        # for nan data
        


def make_sentiment_features_NLTK(df):
    """Make a dataframe including text sentiment features using NLTK Vader"""
    
    sid = SentimentIntensityAnalyzer()
    
    df_time = df.iloc[:, 0:1]
    df_sen = df.iloc[:, 2:22].applymap(lambda x: text_sentiment_NLTK(x, sid))
    
    # Concat to single data frame
    df_feature = pd.concat([df_time, df_sen], axis=1, sort=False)

    return df_feature



###################################################
# Machine learning functions

def ml_random_forest(df_x, df_y):
    """Random forest model"""
    
    # Save model training variable to global envirnoment
    global x_train, x_test, y_train, y_test
    global y_pred_train, y_pred
    
    # Training and test set split
    test_date = datetime.datetime(2020, 6, 1)

    # Define train / test data set
    x_train = df_x[df_x.index < test_date]         # Features
    x_test = df_x[df_x.index >= test_date]
    
    y_train = df_y[df_y.index < test_date]       # Labels
    y_test = df_y[df_y.index >= test_date]
    

    # Define model parameters
    rf = RandomForestClassifier(
            n_estimators = 2000,        # number of trees
            max_features = "sqrt",
            # min_impurity_decrease = 0.007,    # Decieded by CV
            n_jobs = -1
        )
    
    # Cross validation parameters for minimum split cost
    param_grid = {
        "min_impurity_decrease": [10 ** (i / 5.0) for i in range(-10, -26, -1)]
    }
    grid_search = GridSearchCV(estimator = rf, param_grid = param_grid, 
                              cv = 5, n_jobs = -1, verbose = 10)
    
    # CV and model fit
    grid_search.fit(x_train, y_train)
    
    # Best fit, model on whole data sets
    best_rf = grid_search.best_estimator_
    
    # Training error
    y_pred_train = best_rf.predict(x_train)
    print("Train Accuracy:", metrics.accuracy_score(y_train, y_pred_train))
    
    # Predict on test set
    y_pred = best_rf.predict(x_test)
    print("Test Accuracy:", metrics.accuracy_score(y_test, y_pred))

    # Feature names
    features_name = list(x_train.columns.values)

    return best_rf, grid_search, features_name



def plot_feature_important(model, features_name):
    """Show the relative importance of each feature"""
    
    importance = model.feature_importances_
    sort_index = np.argsort(importance)[::-1]
    
    max_importance = max(importance)
    relative_importance = importance / max_importance * 100
    
    xlabels = np.array(features_name)
    
    # Plot
    plt.figure()
    plt.title("Feature Relative Importance")
    plt.bar(
        range(len(relative_importance)), 
        height = relative_importance[sort_index],
        color="r", 
        align="center"
    )
    # plt.xticks(range(len(importance)), xlabels[sort_index])
    plt.show()
    
    
    # Table
    df = pd.DataFrame(data = {
        "features": xlabels[sort_index], 
        "relative_importance": relative_importance[sort_index],
        "importance": importance[sort_index], 
    })

    return df


#%% ###################################################
# Main

# Text data
df = concat_text_data()             # Load
df = validate_text_data(df)         # validate
change_text_date_format(df)

# Stock data
df_spy = read_stock_data()          # Load
pre_process_stock_data(df_spy)      # Pre-process



#%% text analytics, TextBlob sentiment
df_feature_textblob_sentiment = make_sentiment_features_textblob(df)



#%% text analytics, NLTK sentiment
df_feature_NLTK_sentiment = make_sentiment_features_NLTK(df)



#%% random forest model 1, TextBlob prediction
df_all_1 = df_feature_textblob_sentiment.set_index('date').join(df_spy.set_index('date'), how = "inner")

best_rf, grid_search, features_name = ml_random_forest(
    df_all_1.iloc[:, 0:40], 
    df_all_1["direction_up_next_1"]
)
# For stock price direction, use ["direction_up_next_1"]
# For trade volume size, use ["volume_large_next_1"]



#%% random forest model 2, NLTK prediction
df_all_2 = df_feature_NLTK_sentiment.set_index('date').join(df_spy.set_index('date'), how = "inner")

best_rf, grid_search, features_name = ml_random_forest(
    df_all_2.iloc[:, 0:20], 
    df_all_2["direction_up_next_1"]
)



#%% random forest model 3, NLTK prediction using contents only
df_all_3 = df_feature_NLTK_sentiment.set_index('date').join(df_spy.set_index('date'), how = "inner")

best_rf, grid_search, features_name = ml_random_forest(
    df_all_3.iloc[:, [1, 14, 15, 16, 17 ,18 ,19]], 
    df_all_3["direction_up_next_1"]
)



#%% model summary
df_importance = plot_feature_important(best_rf, features_name)
print(df_importance)



#%% 



#%% Testing Only (More confident cutoff)

# =============================================================================
# def prob_cut_off(x, low_cut, up_cut):
#     if (x < low_cut):
#         return False, True            # False
#     elif (x >= up_cut):
#         return True, True            # True
#     else:
#         return True, False            # No conclusion
# 
# 
# df_pred_prob = pd.DataFrame(best_rf.predict_proba(x_test), columns = ["F_prob", "T_prob"])
# 
# result = df_pred_prob["F_prob"].apply(lambda x: prob_cut_off(x, 0.7, 0.3))
# df_pred_prob["result"] = result.apply(lambda x: x[0])
# df_pred_prob["has_result"] = result.apply(lambda x: x[1])
# 
# df_pred_prob["has_result"].mean()
# 
# a = df_pred_prob["has_result"]
# 
# print(metrics.confusion_matrix(np.array(y_test)[a], df_pred_prob["result"][a]))
# print(metrics.accuracy_score(np.array(y_test)[a], df_pred_prob["result"][a]))
# 
# =============================================================================
