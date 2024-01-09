import dash_html_components as html
import dash_core_components as dcc

import pandas as pd
import pathlib
import time
import requests
from pandas.io.json import json_normalize


PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
df_tickers = pd.read_csv(DATA_PATH.joinpath("df_tickers.csv"))

def write_csv(df):
    #df = df.append(rows, ignore_index = True)
    df.to_csv(DATA_PATH.joinpath("df_tickers.csv"),index=False)


def stock_historical_data (symbol, start_date, end_date):
    fd = int(time.mktime(time.strptime(start_date, "%Y-%m-%d")))
    td = int(time.mktime(time.strptime(end_date, "%Y-%m-%d")))
    #td = int(time.mktime(end_date))
    data = requests.get('https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/bars-long-term?ticker={}&type=stock&resolution=D&from={}&to={}'.format(symbol, fd, td)).json()
    if data is not None:
        df = json_normalize(data['data'])
        df['tradingDate'] = pd.to_datetime(df.tradingDate.str.split("T", expand=True)[0])
        df.columns = df.columns.str.title()
        df.rename(columns={'Tradingdate':'TradingDate'}, inplace=True)
    return df

def stock_analysis (symbol):
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/rating/detail/single?ticker={}&fType=TICKER'.format(symbol)).json()
    df = json_normalize(data)
    return df

def dividend_history (symbol):
    data = requests.get('https://apipubaws.tcbs.com.vn/tcanalysis/v1/company/{}/dividend-payment-histories?page=0&size=10'.format(symbol)).json()
    df = json_normalize(data['listDividendPaymentHis']).drop(columns=['no', 'ticker'])
    df.rename(columns={'cashDividendPercentage':'Devidend %'}, inplace=True)
    df.rename(columns={'cashYear':'Year %'}, inplace=True)
    df.rename(columns={'exerciseDate':'Date %'}, inplace=True)
    df.rename(columns={'issueMethod':'Method'}, inplace=True)
    return df



def Header(app):
    return html.Div([get_header(app), html.Br([]), get_menu()])


def get_header(app):
    header = html.Div(
        [
            html.Div(
                [
                    html.A(
                        html.Img(
                            src=app.get_asset_url("dash-financial-logo.png"),
                            className="logo",
                        ),
                        href="https://plotly.com/dash",
                    ),
                    html.A(
                        html.Button(
                            "Enterprise Demo",
                            id="learn-more-button",
                            style={"margin-left": "-10px"},
                        ),
                        href="https://plotly.com/get-demo/",
                    ),
                    html.A(
                        html.Button("Source Code", id="learn-more-button"),
                        href="https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-financial-report",
                    ),
                ],
                className="row",
            ),
            html.Div(
                [
                    html.Div(
                        [html.H5("Vietnam Stocks Investment")],
                        className="seven columns main-title",
                    ),
                    html.Div(
                        [
                            dcc.Link(
                                "Full View",
                                href="/dash-financial-report/full-view",
                                className="full-view-link",
                            )
                        ],
                        className="five columns",
                    ),
                ],
                className="twelve columns",
                style={"padding-left": "0"},
            ),
        ],
        className="row",
    )
    return header


def get_menu():
    menu = html.Div(
        [
            dcc.Link(
                "Overview",
                href="/dash-financial-report/overview",
                className="tab first",
            ),
            dcc.Link(
                "Stock Performance",
                href="/dash-financial-report/price-performance",
                className="tab",
            ),
            dcc.Link(
                "Ticker Chart",
                href="/dash-financial-report/portfolio-management",
                className="tab",
            ),
            dcc.Link(
                "Trading Report", href="/dash-financial-report/fees", className="tab"
            ),
            dcc.Link(
                "Distributions",
                href="/dash-financial-report/distributions",
                className="tab",
            ),
            dcc.Link(
                "News & Reviews",
                href="/dash-financial-report/news-and-reviews",
                className="tab",
            ),
        ],
        className="row all-tabs",
    )
    return menu


def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    html_row = []
    for col in df.columns:
        html_row.append(html.Td([col]))
    table = []
    table.append(html.Tr(html_row))
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table

