import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from utils import Header, make_dash_table
import utils as unil
import pandas as pd
import pathlib

import requests
from pandas.io.json import json_normalize
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta as rd
import pandas_ta as ta
import numpy as np


# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../data").resolve()

def load_dividend_history (symbol):
    return unil.dividend_history(symbol)

def weighted_average(df, value, weight):
    val = df[value]
    wt = df[weight]
    return (val * wt).sum() / wt.sum()

def load_stock_value(symbol):
    print("load_stock_value start", dt.now().strftime("%m/%d/%Y, %H:%M:%S"))
    df = pd.DataFrame(columns=['Name','Value', 'Description'], dtype=object)
        
    stock_data = unil.stock_analysis(symbol)
    Price = stock_data.iloc[-1]['price']
    PE = stock_data.iloc[-1]['priceToEarning']
    PB = stock_data.iloc[-1]['priceToBook']
    ROE = stock_data.iloc[-1]['roe']
    ROA = stock_data.iloc[-1]['roa']
    DoE = stock_data.iloc[-1]['debtOnEquity']
    
    EPS = 0
    if PE is not None and Price is not None:
        EPS = Price /PE
  
    df.loc[0] = ["EPS","{:0,.1f}".format(EPS),"Earning Per Share"]
    if PE is not None:
        df.loc[1] = ["PE","{:0,.1f}".format(PE),"Price to Earning"]
    if PB is not None:
        df.loc[2] = ["PB","{:0,.1f}".format(PB),"Price to Book"]
    if ROE is not None:
        df.loc[3] = ["ROE","{0:.0%}".format(ROE),"Return On Equity"]
    if ROA is not None:
        df.loc[4] = ["ROA","{0:.0%}".format(ROA),"Return on total assets"]
    if DoE is not None:
        df.loc[5] = ["DoE","{0:.0%}".format(DoE),"Debt on Equity"]
    
    print("load_stock_value end", dt.now().strftime("%m/%d/%Y, %H:%M:%S"))
    return df


#SMA BUY SELL
#Function for buy and sell signal
def buy_sell(data):
    signalBuy = []
    signalSell = []
    position = False 

    for i in range(len(data)):
        if data['Close'][i] > data['SMA20'][i]:
            if position == False :
                signalBuy.append(data['Close'][i])
                signalSell.append(np.nan)
                position = True
                #print("signalBuy", signalBuy)
            else:
                signalBuy.append(np.nan)
                signalSell.append(np.nan)
        elif data['Close'][i] < data['SMA20'][i]:
            if position == True:
                signalBuy.append(np.nan)
                signalSell.append(data['Close'][i])
                position = False
                #print("signalSell", signalSell)
            else:
                signalBuy.append(np.nan)
                signalSell.append(np.nan)
        else:
            signalBuy.append(np.nan)
            signalSell.append(np.nan)

    # for i in range(len(data)):
    #     if data['SMA20'][i] > data['SMA50'][i]:
    #         if position == False :
    #             signalBuy.append(data['Close'][i])
    #             signalSell.append(np.nan)
    #             position = True
    #             #print("signalBuy", signalBuy)
    #         else:
    #             signalBuy.append(np.nan)
    #             signalSell.append(np.nan)
    #     elif data['SMA20'][i] < data['SMA50'][i]:
    #         if position == True:
    #             signalBuy.append(np.nan)
    #             signalSell.append(data['Close'][i])
    #             position = False
    #             #print("signalSell", signalSell)
    #         else:
    #             signalBuy.append(np.nan)
    #             signalSell.append(np.nan)
    #     else:
    #         signalBuy.append(np.nan)
    #         signalSell.append(np.nan)
    
    return pd.Series([signalBuy, signalSell])


def load_stock_price_history(ticker):
    df_graph = unil.stock_historical_data(symbol=ticker, start_date=(dt.now() + rd(months=-12)).strftime('%Y-%m-%d'), end_date=dt.now().strftime('%Y-%m-%d'))
    
    df_graph['SMA20'] = ta.sma(df_graph['Close'],20)
    df_graph['SMA50'] = ta.sma(df_graph['Close'],50)
    df_graph['SMA100'] = ta.sma(df_graph['Close'],100)
    df_graph['Buy_Signal_price'], df_graph['Sell_Signal_price'] = buy_sell(df_graph)

    figure1 = {
                "data": [
                    go.Scatter(
                        x=df_graph["TradingDate"],
                        y=df_graph["Close"],
                        line={"color": "#97151c"},
                        mode="lines",
                        name="Close",
                    ),
                    go.Scatter(
                        x=df_graph["TradingDate"],
                        y=df_graph["Buy_Signal_price"],
                        line={"color": "#0000FF"},
                        mode = "markers",
                        name="Buy",
                    ),
                    go.Scatter(
                        x=df_graph["TradingDate"],
                        y=df_graph["Sell_Signal_price"],
                        line={"color": "#FF0000"},
                        mode = "markers",
                        name="Sell",
                    ),
                    #go.scatter(x=df_graph["TradingDate"] , y = df_graph['Sell_Signal_price'] , label = 'Sell' , marker = 'v', color = 'red',alpha =1 ),
                    go.Scatter(
                        x=df_graph["TradingDate"],
                        #y = df_graph["Close"].rolling(20).mean(), # Pandas SMA
                        y=df_graph["SMA20"],
                        line={"color": "#3E86AB"},
                        mode="lines",
                        name = "SMA20",
                    ),
                    go.Scatter(
                        x=df_graph["TradingDate"],
                        #y = df_graph["Close"].rolling(50).mean(), # Pandas SMA
                        y=df_graph["SMA50"],
                        line={"color": "#FFA500"},
                        mode="lines",
                        name = "SMA50",
                    ),
                    # go.Scatter(
                    #     x=df_graph["TradingDate"],
                    #     #y = df_graph["Close"].rolling(100).mean(), # Pandas SMA
                    #     y=df_graph["SMA100"],
                    #     line={"color": "#A020F0"},
                    #     mode="lines",
                    #     name = "SMA100",
                    # ),
                  
                ],
                "layout": go.Layout(
                    autosize=True,
                    width=700,
                    height=300,
                    font={"family": "Raleway", "size": 10},
                    margin={
                        "r": 30,
                        "t": 30,
                        "b": 30,
                        "l": 30,
                    },
                    showlegend=True,
                    titlefont={
                        "family": "Raleway",
                        "size": 10,
                    },
                    xaxis={
                        "autorange": True,
                        "range": [
                            dt.now() + rd(months=-12),
                            dt.now(),
                        ],
                        "rangeselector": {
                            "buttons": [
                                {
                                    "count": 1,
                                    "label": "1M",
                                    "step": "month",
                                    "stepmode": "backward",
                                },
                                {
                                    "count": 3,
                                    "label": "3M",
                                    "step": "month",
                                    "stepmode": "backward",
                                },
                                {
                                    "count": 6,
                                    "label": "6M",
                                    "step": "month",
                                },
                                {
                                    "count": 12,
                                    "label": "12M",
                                    "step": "month",
                                    "stepmode": "backward",
                                },
                                {
                                    "label": "All",
                                    "step": "all",
                                },
                            ]
                        },
                        "showline": True,
                        "type": "date",
                        "zeroline": False,
                    },
                    yaxis={
                        "autorange": True,
                        "range": [
                            10,
                            100,
                        ],
                        "showline": True,
                        "type": "linear",
                        "zeroline": False,
                    },
                ),
            }

    figure2 = {
                "data": [
                    go.Candlestick(
                        x=df_graph["TradingDate"],
                        open=df_graph["Open"],
                        close=df_graph["Close"],
                        high=df_graph["High"],
                        low=df_graph["Low"],
                        name="Candles",
                        hovertext=[df_graph["Volume"]],
                    ),
                ],
                "layout": go.Layout(
                    autosize=True,
                    width=700,
                    height=400,
                    font={"family": "Raleway", "size": 10},
                    margin={
                        "r": 30,
                        "t": 30,
                        "b": 30,
                        "l": 30,
                    },
                    showlegend=True,
                    titlefont={
                        "family": "Raleway",
                        "size": 10,
                    },
                    xaxis={
                        "autorange": True,
                        "range": [
                            dt.now() + rd(months=-12),
                            dt.now(),
                        ],
                        "rangeselector": {
                            "buttons": [
                                {
                                    "count": 1,
                                    "label": "1M",
                                    "step": "month",
                                    "stepmode": "backward",
                                },
                                {
                                    "count": 3,
                                    "label": "3M",
                                    "step": "month",
                                    "stepmode": "backward",
                                },
                                {
                                    "count": 6,
                                    "label": "6M",
                                    "step": "month",
                                },
                                {
                                    "count": 12,
                                    "label": "12M",
                                    "step": "month",
                                    "stepmode": "backward",
                                },
                                {
                                    "label": "All",
                                    "step": "all",
                                },
                            ]
                        },
                        "showline": True,
                        "type": "date",
                        "zeroline": False,
                    },
                    yaxis={
                        "autorange": True,
                        "range": [
                            10,
                            100,
                        ],
                        "showline": True,
                        "type": "linear",
                        "zeroline": False,
                    },
                ),
            }
    return figure1,figure2

def create_layout(app):
    return html.Div(
        [
            Header(app),
            # page 3
            html.Div(
                [
                     # Row 1
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6("History", className="subtitle padded"),
                                    dcc.Dropdown(
                                        id="dropdown-stock-list",
                                        options=[{'label': row[0], 'value': row[0]} for index, row in unil.df_tickers.iterrows()],
                                        value='HPG',
                                        clearable=False,
                                        ),
                                    dcc.Graph(
                                        id="graph-4",
                                        config={"displayModeBar": False},
                                    ),
                                    dcc.Graph(
                                        id="graph-5",
                                        config={"displayModeBar": True},
                                    ),
                                ],
                                className="twelve columns",
                            )
                        ],
                        className="row ",
                    ),
                    
                    # Row 2
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6(
                                        ["Company information / Dividend"],
                                        className="subtitle tiny-header padded",
                                    )
                                ],
                                className=" twelve columns",
                            ), 

                             # Row 3
                            html.Div(
                                [
                                    html.Div(
                                        id="div-dividend",
                                        className="six columns"),
                                ],
                            ),

                            html.Div(
                                [
                                    html.Div(
                                        id="div-company-value",
                                        className="six columns"),
                                ],
                            ),
                        ],
                        className="row ",
                    ),

                     # Row 1
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6("News", className="subtitle padded"),
                                    html.A("https://s.cafef.vn/tin-doanh-nghiep/pdr/Event.chn", href='https://s.cafef.vn/tin-doanh-nghiep/pdr/Event.chn', target="_blank"),
                                ],
                                className="twelve columns",
                            )
                        ],
                        className="row ",
                    ),
                   
                ],
                className="sub_page",
            ),
        ],
        className="page",
    )
