# FINA_4350_Mid_term_project

This project attempts to predict the performance of SPY ETF using financial news headlines on Reuters webpage on the previous trading day.

## Data
News headlines between October 2018 and September 2020 are scraped from the Reuters financial news homepage (https://www.reuters.com/finance).

Past versions of the webpage are retrieved from the Internet Archive (https://archive.org).

The adjusted closing price and trade volume of SPY ETF is retrieved from Yahoo Finance (https://finance.yahoo.com/quote/SPY/history/).


## Analysis
Sentiment analysis is performed on the text data using TextBlob and NLTK Vader. 

A random forest model is fitted to predict the direction of the stock price and the relative size of the daily trade volume.


## Files

|     Filename                        |     Description                                               |
|-------------------------------------|---------------------------------------------------------------|
|     Step_1_scrape_web.py            |     Scrape text data from web and save into   CSV files       |
|     Step_2_analyse_data.py          |     Data pre-processing and fitting random   forest models    |
|     web_data/web_data_yyyymm.csv    |     Text data from Reuters financial news   homepage          |
|     SPY.csv                         |     Historic ETF prices from Yahoo Finance                    |

## What's More

For more detials, please see the [full article](./Report.pdf).

