import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from utils import Header, make_dash_table
import pandas as pd
import pathlib

import utils as util

import requests
from pandas.io.json import json_normalize
from dash.dependencies import Input, Output,State

from datetime import datetime as dt
#from datetime import timedelta
from dateutil.relativedelta import relativedelta as rd

from io import BytesIO
# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()


def vnindex_stock_down(rate, start_date, end_date):
    print("vnindex_stock_down start", dt.now().strftime("%m/%d/%Y, %H:%M:%S"))
    df = pd.DataFrame(columns=['Ticker', 'Max Price', 'Current Price', 'Down %'], dtype=object)
    #df = []
    for index, row in util.df_tickers.iterrows():
        stock_data = util.stock_historical_data(row[0],start_date,end_date)
        price_max = max(stock_data['Close'])
        #print(index)
        #print(row[0])
        down_percent = 1 - (stock_data.iloc[-1]['Close'] / price_max)
        #print(stock_data.iloc[-1]['Close'])
        if down_percent > rate/100:
            #print(row[0])
            df.loc[index] = [row[0],"{:0,.0f}".format(price_max),"{:0,.0f}".format(stock_data.iloc[-1]['Close']), "{0:.0%}".format(down_percent)]
    df = df.sort_values('Down %', ascending=False)
    print("vnindex_stock_down start", dt.now().strftime("%m/%d/%Y, %H:%M:%S"))
    return df

def vnindex_stock_value(PEValue,PBValue):
    print("vnindex_stock_value start", dt.now().strftime("%m/%d/%Y, %H:%M:%S"))
    df = pd.DataFrame(columns=['Ticker','Price','PE', 'EPS', 'PB','ROE','ROA','DoE'], dtype=object)
    #df = []
    for index, row in util.df_tickers.iterrows():
        stock_data = util.stock_analysis(row[0])
        Price = stock_data.iloc[-1]['price']
        PE = stock_data.iloc[-1]['priceToEarning']
        PB = stock_data.iloc[-1]['priceToBook']
        ROE = stock_data.iloc[-1]['roe']
        ROA = stock_data.iloc[-1]['roa']
        DoE = stock_data.iloc[-1]['debtOnEquity']
        if PE is not None and Price is not None:
          EPS = Price /PE
          if PE < PEValue and PB < PBValue:
            df.loc[index] = [row[0],"{:0,.0f}".format(Price),"{:0,.1f}".format(PE),"{:0,.1f}".format(EPS),"{:0,.1f}".format(PB),"{0:.0%}".format(ROE),"{0:.0%}".format(ROA),"{:0,.0%}".format(DoE) ]
    
    df['PE'] = df['PE'].astype(float)
    df = df.sort_values('PE', ascending=True)
    print("vnindex_stock_value end", dt.now().strftime("%m/%d/%Y, %H:%M:%S"))
    return df


def load_stock_down(month_period,down_percent):
    print("load_stock_down start", dt.now().strftime("%m/%d/%Y, %H:%M:%S"))
    df_stock_down = vnindex_stock_down(rate=down_percent, start_date=(dt.now() + rd(months=-month_period)).strftime('%Y-%m-%d'), end_date=dt.now().strftime('%Y-%m-%d'))
    print("load_stock_down end", dt.now().strftime("%m/%d/%Y, %H:%M:%S"))
    return df_stock_down


def create_layout(app):
        
    return html.Div(
        [
            Header(app),
            # page 2
            html.Div(
                [
                    # Row
                    html.Div(
                        [
                            
                            html.Div(
                                [
                                    html.H6(
                                        ["Stock Values"], 
                                        className="subtitle padded",
                                    ),
                                    
                                    html.Div(
                                        [
                                            
                                            dcc.Dropdown(
                                            id="dropdown-pe",
                                            clearable=False,
                                            options=[
                                                {'label': '-', 'value': -1},
                                                {'label': 'PE < 2', 'value': 2},
                                                {'label': 'PE < 3', 'value': 3},
                                                {'label': 'PE < 5', 'value': 5},
                                                {'label': 'PE < 8', 'value': 8},
                                                {'label': 'PE < 13', 'value': 13},
                                                {'label': 'PE < 21', 'value': 21},
                                            ],
                                            value=-1,
                                            style={'display': "inline-block",'float': 'left','width': '50%'}
                                            ),
                                            dcc.Dropdown(
                                            id="dropdown-pb",
                                            clearable=False,
                                            options=[
                                                {'label': '-', 'value': -1},
                                                {'label': 'PB < 0.5', 'value': 0.5},
                                                {'label': 'PB < 1', 'value': 1},
                                                {'label': 'PB < 1.5', 'value': 1.5},
                                                {'label': 'PB < 2', 'value': 2},
                                                {'label': 'PB < 3', 'value': 3},
                                                {'label': 'PB < 4', 'value': 4},
                                            ],
                                            value=-1,
                                            style={'display': "inline-block",'float': 'left','width': '50%'}
                                            ),                     
                                        ],
                                        style= {'width': '100%', 'display': 'inline-block'},
                                    ),
                                    
                                    html.Div(id="div-stock-value"),

                                ],
                                className="six columns",
                            ),
                            
                            html.Div(
                                [
                                    html.H6(
                                        ["Down Stocks"],
                                        className="subtitle padded",
                                    ),
                                    html.Div(
                                        [
                                            dcc.Dropdown(
                                                id="dropdown-month-period",
                                                clearable=False,
                                                options=[
                                                    {'label': '-', 'value': -1},
                                                    {'label': '1 month', 'value': 1},
                                                    {'label': '2 months', 'value': 2},
                                                    {'label': '3 months', 'value': 3},
                                                    {'label': '4 months', 'value': 4},
                                                    {'label': '5 months', 'value': 5},
                                                    {'label': '6 months', 'value': 6},
                                                ],
                                                value=-1,
                                                style={'display': "inline-block",'float': 'left','width': '60%'}
                                            ),
                                            dcc.Input(
                                                id="input_down_percent", type="number",
                                                min=10, max=100, step=10,
                                                value=30,
                                                style={'display': "inline-block",'float': 'left','width': '30%'}
                                            ),                        
                                        ],
                                        style= {'width': '100%', 'display': 'inline-block'},
                                    ),
                                    
                                    html.Div(id="div-stock-down"),
                                ],
                                className="six columns",
                            ),
                           
                        ],
                        className="row ",
                    ),
                  
                ],
                className="sub_page",
            ),
        ],
        className="page",

    )







