#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 15:03:49 2018

@author: AliciaSu
"""

'''
This notebook uses PCA (principle component analysis) to find factors that explain 
the majority of the variance in the US Equity data.

Each series is regressed against the first N components and weighted inversely to the zscore of the residuals.

Built on Quantopia's API platform.

'''

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import statsmodels.api as sm


def initialize(context):
    set_universe(universe.DollarVolumeUniverse(
        floor_percentile=95.0, ceiling_percentile=100.0))
    set_slippage(slippage.FixedSlippage(spread=0.00))
    set_commission(commission.PerShare(cost=0.0, min_trade_cost=0.0))
    context.lookback = 30
    context.leverage = 1.0
    context.n_components = 3
    context.min_z = 2.0
    schedule_function(trade,
                      date_rule=date_rules.week_start(),
                      time_rule=time_rules.market_open(minutes=20))
    

    
def handle_data(context, data):
    record(leverage=context.account.leverage,
           exposure=context.account.net_leverage)
    
def trade(context, data):                      
    observations = np.log(history(context.lookback, '1d', 'price').dropna(axis=1))
    try:
        models = get_PCA_regressions(observations, n_factors=context.n_components)
        resids = pd.DataFrame({sym: models[sym].resid for sym in models})
        zscores = Zscore(resids).iloc[-1]
        weights = zscores[zscores.abs() > context.min_z]
        weights *= (context.leverage / weights.abs().sum())
        for stock in data:
            if stock in weights.index:
                order_target_percent(stock, -weights[stock])
            else:
                order_target(stock, 0)
    except Exception as e:
        log.debug(e)
        
  
def get_PCA_regressions(data, n_factors=3):
    pca = PCA()
    model = pca.fit(data)
    factors = data.dot(model.components_.T)[range(n_factors)]
    factors = sm.add_constant(factors)
    models = {sym: sm.OLS(data[sym], factors).fit()
              for sym in data.columns}
    return models

def Zscore(X):
    return (X - X.mean()) / X.std()
