#Based off Bobby's code, but made generic so you can feed two dates and a list of stocks
#and the function returns cointegrated pairs. See usage at the bottom of the file.

import numpy as np
import pandas as pd
import statsmodels
from statsmodels.tsa.stattools import coint
import matplotlib.pyplot as plt

#function to find cointegrated pairs
def find_cointegrated_pairs(data):
    n = data.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    keys = data.keys()
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            S1 = data[keys[i]]
            S2 = data[keys[j]]
            result = coint(S1, S2)
            score = result[0]
            pvalue = result[1]
            score_matrix[i, j] = score
            pvalue_matrix[i, j] = pvalue
            if pvalue < 0.05:
                pairs.append((keys[i], keys[j]))
    return score_matrix, pvalue_matrix, pairs

import datetime as dt
import pandas_datareader.data as web

def coint_daterange(start_date,end_date, asset_list):
    stocks = asset_list
    ls_key = 'Adj Close'
    start= start_date
    end= end_date
    df=web.DataReader(stocks,'yahoo',start,end)
    cleanData = df[ls_key]
    cleanData.head()
    scores, pvalues, pairs = find_cointegrated_pairs(cleanData)
    return pairs

stocks_to_check = ['SPY','AAPL','ADBE','SYMC','EBAY','MSFT','QCOM', 'HPQ','JNPR','AMD','IBM']
this_pairs = coint_daterange(dt.datetime(2016,1,9), dt.datetime(2017,1,30), stocks_to_check)
print(this_pairs)
