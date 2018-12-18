#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 19:33:06 2018

@author: AliciaSu
"""

import pandas as pd
from pandas import DataFrame
import argparse
import quandl
import pandas_datareader as web
from time import sleep
import datetime as dt
import sys
 

#data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')

#table = data[0]
#table.head()

#sliced_table = table[1:]
#header = table.iloc[0]
#corrected_table = sliced_table.rename(columns=header)
#corrected_table.head()

#tickers = corrected_table['Symbol'].tolist()
#print (tickers)

def get_sp500_data(start=dt.datetime.strptime("2007-12-01", "%Y-%m-%d"),
                   end=dt.datetime.strptime("2017-12-01", "%Y-%m-%d"), use_quandl=True, adjust=True, inner=True,
                   sleeptime=0.1, verbose=True):
    """Fetches S&P 500 data
     
    args:
        start: datetime; The earliest possible date
        end: datetime; The last possible date
        use_quandl: bool; Whether to fetch data from Quandl (reverts to Google if False)
        adjust: bool; Whether to use adjusted close (only works with Quandl)
        inner: bool; Whether to use an inner join or outer join when combining series (inner has no missing data)
        sleeptime: int; How long to sleep between fetches
        verbose: bool; Whether to print a log while fetching data
     
    return:
        DataFrame: Contains stock price data
    """
    
    join = "outer"
    if inner:
        join = "inner"
     
    symbols_table = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
                                 header=0)[0]
    symbols = list(symbols_table.loc[:, "Symbol"])
 
    sp500 = None
    for s in symbols:
        sleep(sleeptime)
        if verbose:
            print("Processing: " + s + "...", end='')
        try:
            if use_quandl:
                s_data = quandl.get("WIKI/" + s, start_date=start, end_date=end)
                if adjust:
                    s_data = s_data.loc[:, "Adj. Close"]
                else:
                    s_data = s_data.loc[:, "Close"]
            else:
                s_data = web.DataReader(s, "google", start, end).loc[:, "Close"]
            s_data.name = s
            s_data.dropna()
            if s_data.shape[0] > 1:
                if sp500 is None:
                    sp500 = DataFrame(s_data)
                else:
                    sp500 = sp500.join(s_data, how="outer")
                if verbose:
                    print(" Got it! From", s_data.index[0], "to", s_data.index[-1])
            else:
                if verbose:
                    print(" Sorry, but not this one!")
        except Exception:
            if verbose:
                print(" Sorry, but not this one!")
 
    badsymbols = list(set(s) - set(sp500.columns))
    if verbose and len(badsymbols) > 0:
        print("There were", len(badsymbols), "symbols for which data could not be obtained.")
        print("They are:", ", ".join(badsymbols))
     
    return sp500


df=get_sp500_data()
#df.head()

import tkinter as tk
from tkinter import filedialog

root= tk.Tk()

canvas1 = tk.Canvas(root, width = 300, height = 300, bg = 'lightsteelblue2', relief = 'raised')
canvas1.pack()

def exportCSV ():
    global df
    
    export_file_path = filedialog.asksaveasfilename(defaultextension='.csv')
    df.to_csv (export_file_path, header=True)

saveAsButton_CSV = tk.Button(text='Export CSV', command=exportCSV, bg='green', fg='white', font=('helvetica', 12, 'bold'))
canvas1.create_window(150, 150, window=saveAsButton_CSV)

root.mainloop()