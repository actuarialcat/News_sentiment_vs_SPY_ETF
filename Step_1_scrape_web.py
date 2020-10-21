#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 18:41:47 2020

@author: Jackson
"""

import requests
#from lxml import html
from bs4 import BeautifulSoup

import datetime
import pandas as pd 
from pathlib import Path

###################################################
# Global Param

ARCHIVE_API_URL = "https://archive.org/wayback/available?"
WEBSITE_URL = "https://www.reuters.com/finance"

CLOSEST_TIME = "120000"       # hhmmss

OUTPUT_PATH = ""
OUTPUT_FILENAME_PREFIX = "web_data_"



###################################################
# Web-interface functions

def initiate_session():
    """Start a web session"""
    
    session_requests = requests.session()
    
    return session_requests



def find_closest_url(session_requests, date, time):
    """Find the first availble webpage on the specific date"""
    
    # API request paramenters
        # date : yyyymmdd
        # time : hhmmss
    
    # create API request
    url_api = ARCHIVE_API_URL + "url=" + WEBSITE_URL + "&timestamp=" + date + time

    # retrieve API JSON output
    result = session_requests.get(url_api, timeout = 10).json()
    
    # extract the URL to target website
    archive_web_url = result["archived_snapshots"]["closest"]["url"]
    timestamp = result["archived_snapshots"]["closest"]["timestamp"]
    
    return (archive_web_url, timestamp)



def scrape_html(session_requests, url):
    """Input session and URL, return scaped html data"""
    
    result = session_requests.get(url, timeout = 10)
    soup = BeautifulSoup(result.text, "lxml")
    
    return soup



###################################################
# Data Extraction Functions

def extract_details(soup):
    """Extract the contents on the webpage"""

    # Main story
    s_main = soup.find("article", {"class": "story featured-article no-border-bottom"})
    s_main_content = s_main.find("div", {"class": "story-content"})

    main_title = s_main_content.find("", {"class": "story-title"}).get_text().strip()
    main_content = s_main_content.p.get_text().strip()


    # Featured stories x3
    s_feature = soup.find("div", {"class": "news-headline-list small news-horizontal-tri"})
    s_feature_content = s_feature.find_all("article")

    feature_title = [""] * 3
    for i in range(3):
        feature_title[i] = s_feature_content[i].find("", {"class": "story-title"}).get_text().strip()
    
    
    # Video x3
    s_video = soup.find("section", {"class": "module mod-video mod-video-dark mod-video-horizontal"})
    s_video_content = s_video.find_all("div", {"class": "video group"})

    video_title = [""] * 3
    for i in range(3):
        video_title[i] = s_video_content[i].find("h3", {"class": "video-heading"}).a.get_text().strip()
    
    
    # Stories x6
    s_stories = soup.find_all("div", {"class": "news-headline-list"})
    s_stories_content = s_stories[2].find_all("article", {"class": "story"})
    
    stories_title = [""] * 6
    stories_content = [""] * 6
    for i in range(6):
        stories_title[i] = s_stories_content[i].find("", {"class": "story-title"}).get_text().strip()
        stories_content[i] = s_stories_content[i].p.get_text().strip()


    # make dataframe
    df_web_content = pd.DataFrame(data = {
        "main_title": [main_title], 
        "main_content": [main_content], 
        "feature_title_0": feature_title[0],
        "feature_title_1": feature_title[1],
        "feature_title_2": feature_title[2],
        "video_title_0": video_title[0],
        "video_title_1": video_title[1],
        "video_title_2": video_title[2],
        "stories_title_0": stories_title[0],
        "stories_title_1": stories_title[1],
        "stories_title_2": stories_title[2],
        "stories_title_3": stories_title[3],
        "stories_title_4": stories_title[4],
        "stories_title_5": stories_title[5],
        "stories_content_0": stories_content[0],
        "stories_content_1": stories_content[1],
        "stories_content_2": stories_content[2],
        "stories_content_3": stories_content[3],
        "stories_content_4": stories_content[4],
        "stories_content_5": stories_content[5],
        })
    
    return df_web_content



###################################################
# Date Functions

def generate_date_series(st_year, st_month, st_day, en_year, en_month, en_day):
    """generate string series of dates, exclude last day"""
    
    dt = datetime.datetime(st_year, st_month, st_day)
    end = datetime.datetime(en_year, en_month, en_day)
    step = datetime.timedelta(days = 1)
    
    result = []
    
    while dt < end:
        result.append(dt.strftime("%Y%m%d"))
        dt += step

    return result



###################################################
# Control Functions

def extract_year(year, end_month = 12):
    """Extract data within a year, generate csv file for each month"""

    for i in range(end_month + 1):
        df_web = extract_month(year, i + 1)
        


def extract_month(year, month):
    """Extract data within a month, and output csv"""
    
    # Initialize dataframe
    df_web = pd.DataFrame()
    
    date_series = generate_date_series(year, month, 1, year, month + 1, 1) 
    
    # Loop through all days
    for date in date_series:
        df_web_new = extract_one_day(session_requests, date)
        
        df_web = df_web.append(df_web_new, ignore_index = True, sort=False)
        
        print("Completed: " + date)
    
    # output csv file
    filename = OUTPUT_FILENAME_PREFIX + str(month).zfill(2) + ".csv"
    output_cvs(df_web, filename)
    
    return df_web



def extract_one_day(session_requests, date):
    """Extract a specific date web data"""

    # Parameters
    time = CLOSEST_TIME       # hhmmss
    
    # Extract HTML data
    cloest_web = find_closest_url(session_requests, date, time)
    
    first_url = cloest_web[0]
    timestamp = cloest_web[1]
    
    soup = scrape_html(session_requests, first_url)

    # Extract text data from HTML
    df_web_content = extract_details(soup)
    
    # Create dataframe
    df_timestamp = pd.DataFrame(data = {
        "date": [date], 
        "timestamp": [timestamp]
        })

    df_web = pd.concat([df_timestamp.reset_index(drop=True), df_web_content], axis=1, sort=False)
    
    return df_web



def output_cvs(df, filename):
    """output dataframe into csv file"""
    
    full_filename = Path(OUTPUT_PATH + filename) 
    df.to_csv(full_filename)



#%% ###################################################
# Main

# Initiate session
if ("session_requests" not in globals()):
    global session_requests
    session_requests = initiate_session()
    
    
#%% Scrape all data

extract_year(2020, 9)



#%% Test month
    
df_web = extract_month(2020, 9)


#%% Test day
    
test_date = "20200901"       # yyyymmdd
test_df_web = extract_one_day(session_requests, test_date)








