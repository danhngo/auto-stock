import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from utils import Header, make_dash_table
import pandas as pd
import pathlib
import requests
import utils as util

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

def market_top_mover (report_name): #Value, Losers, Gainers, Volume, ForeignTrading, NewLow, Breakout, NewHigh
    """
    This function returns the list of Top Stocks by one of criteria: 'Value', 'Losers', 'Gainers', 'Volume', 'ForeignTrading', 'NewLow', 'Breakout', 'NewHigh'.
    Args:
        report_name(:obj:`str`, required): name of the report
    """
    ls1 = ['Gainers', 'Losers', 'Value', 'Volume']
    # ls2 = ['ForeignTrading', 'NewLow', 'Breakout', 'NewHigh']
    if report_name in ls1:
        url = 'https://fiin-market.ssi.com.vn/TopMover/GetTop{}?language=vi&ComGroupCode=All'.format(report_name)
    elif report_name == 'ForeignTrading':
        url = 'https://fiin-market.ssi.com.vn/TopMover/GetTopForeignTrading?language=vi&ComGroupCode=All&Option=NetBuyVol&TimeRange=ThreeMonths'
    elif report_name == 'NewLow':
        url = 'https://fiin-market.ssi.com.vn/TopMover/GetTopNewLow?language=vi&ComGroupCode=All&TimeRange=ThreeMonths'
    elif report_name == 'Breakout':
        url = 'https://fiin-market.ssi.com.vn/TopMover/GetTopBreakout?language=vi&ComGroupCode=All&TimeRange=OneWeek&Rate=OnePointFive'
    elif report_name == 'NewHigh':
        url = 'https://fiin-market.ssi.com.vn/TopMover/GetTopNewHigh?language=vi&ComGroupCode=All&TimeRange=ThreeMonths'
    headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
            'DNT': '1',
            'sec-ch-ua-mobile': '?0',
            'X-Fiin-Key': 'KEY',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Fiin-User-ID': 'ID',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'X-Fiin-Seed': 'SEED',
            'sec-ch-ua-platform': 'Windows',
            'Origin': 'https://iboard.ssi.com.vn',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://iboard.ssi.com.vn/',
            'Accept-Language': 'en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7'
            }
    r = requests.get(url, headers=headers).json()

    pd.options.display.float_format = '${:,.2f}'.format

    df = pd.DataFrame(r['items'])
    df = df.drop(columns=['organCode','performance','financial','technical','floorPrice','ceilingPrice','ceilingPrice','o','referencePrice','h','l','priceChange','percentPriceChange','rank','totalRank'])
    #price	sectorName	ticker	value	volume 
    df.rename(columns={"price": "Price", "sectorName": "Sector", "sectorName": "Sector", "ticker": "Ticker", "value": "Value", "volume": "Volume"},inplace=True)
    df.loc[:, "Price"] = df["Price"].map('{:0,.0f}'.format)
    df.loc[:, "Volume"] = (df["Volume"] / 1000000 ).map('{:0,.1f}M'.format)
    df.loc[:, "Value"] = (df["Value"] / 1000000 ).map('{:0,.0f}M'.format) 
    
    if report_name == 'ForeignTrading':
        #foreignBuyValue	foreignBuyVolume	foreignSellValue	foreignSellVolume	
        df.rename(columns={"foreignBuyValue": "Foreign Buy Value", "foreignBuyVolume": "Foreign Buy Volume", "foreignSellValue": "Foreign Sell Value", "foreignSellVolume": "Foreign Sell Volume"},inplace=True)
        df = df.loc[:,['Ticker','Sector','Price','Volume','Value','Foreign Buy Volume','Foreign Buy Value','Foreign Sell Volume','Foreign Sell Value']]
        df = df.sort_values('Foreign Buy Value', ascending=False)

        df.loc[:, "Foreign Buy Value"] = (df["Foreign Buy Value"] / 1000000).map('{:0,.0f}M'.format)
        df.loc[:, "Foreign Buy Volume"] = (df["Foreign Buy Volume"] / 1000000).map('{:0,.1f}M'.format) 
        df.loc[:, "Foreign Sell Value"] = (df["Foreign Sell Value"] / 1000000).map('{:0,.0f}M'.format) 
        df.loc[:, "Foreign Sell Volume"] = (df["Foreign Sell Volume"] / 1000000).map('{:0,.1f}M'.format) 

        
    if report_name == 'Value':
        df = df.sort_values('Value', ascending=False)
        df = df.loc[:,['Ticker','Sector','Price','Volume','Value']]
    if report_name == 'Volume':
        df = df.loc[:,['Ticker','Sector','Price','Volume','Value']]
        df = df.sort_values('Volume', ascending=False)  
    
    df = df.head(40)

    #Store to stock list if found new foreign buy ticker 
    update_csv = False
    if report_name == 'ForeignTrading':
        for i in range(len(df)):
            if not df['Ticker'][i] in util.df_tickers.values:
                #print(df['Ticker'][i])
                df2 = {'Ticker': df['Ticker'][i]}
                util.df_tickers = util.df_tickers.append(df2, ignore_index = True)
                update_csv = True
    if update_csv:          
        print(update_csv)
        util.write_csv(util.df_tickers)
    
    return df

def create_layout(app):
    return html.Div(
        [
            Header(app),
            # page 4
            html.Div(
                [
                    # Row 1
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6("Trading Report", className="subtitle padded"),
                                    dcc.Dropdown(
                                        id="dropdown-report",
                                        options=[
                                                    {'label': 'Value', 'value': 'Value'},
                                                    {'label': 'Volume', 'value': 'Volume'},
                                                    {'label': 'ForeignTrading', 'value': 'ForeignTrading'},
                                                ],
                                        value='ForeignTrading',
                                        clearable=False,
                                        ),
                                    html.Div(
                                        id="div-report",
                                        children=make_dash_table(market_top_mover('ForeignTrading')),
                                        className="twelve columns"),
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
