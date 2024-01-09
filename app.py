# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State
from dash.exceptions import PreventUpdate

from utils import Header, make_dash_table


from pages import (
    Report,
    StockPerformance,
    TickerChart,
    overview,
    distributions,
    newsReviews,
)
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Financial Report"
server = app.server



# Describe the layout/ UI of the app
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)



# Update page
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])

def display_page(pathname):
    if pathname == "/dash-financial-report/price-performance":
        return StockPerformance.create_layout(app)
    elif pathname == "/dash-financial-report/portfolio-management":
        return TickerChart.create_layout(app)
    elif pathname == "/dash-financial-report/fees":
        return Report.create_layout(app)
        #return test.create_layout(app)
    elif pathname == "/dash-financial-report/distributions":
        return distributions.create_layout(app)
    elif pathname == "/dash-financial-report/news-and-reviews":
        return newsReviews.create_layout(app)
    elif pathname == "/dash-financial-report/full-view":
        return (
            overview.create_layout(app),
            StockPerformance.create_layout(app),
            TickerChart.create_layout(app),
            Report.create_layout(app),
            distributions.create_layout(app),
            newsReviews.create_layout(app),
        )
    else:
        return overview.create_layout(app)
app.config.suppress_callback_exceptions = True

@app.callback(
    Output(component_id='div-stock-down', component_property='children'),
    [Input('dropdown-month-period', 'value'),
    Input('input_down_percent', 'value')],
)
def update_stock_down(month_period,down_percent):
    if month_period != -1:
        return make_dash_table(StockPerformance.load_stock_down(month_period,down_percent))  

@app.callback(
    Output(component_id='div-stock-value', component_property='children'),
    [Input('dropdown-pe', 'value'),
    Input('dropdown-pb', 'value')],
)
def update_stock_value(pe,pb):
    if pe != -1 and pb != -1:
        return make_dash_table(StockPerformance.vnindex_stock_value(pe,pb))      

@app.callback(
    [Output(component_id='graph-4', component_property='figure'),
    Output(component_id='graph-5', component_property='figure'),],
    [Input('dropdown-stock-list', 'value')],
)
def update_stock_history(value):
    return TickerChart.load_stock_price_history(value)  

@app.callback(
    [Output(component_id='div-dividend', component_property='children'),
    Output(component_id='div-company-value', component_property='children')],
    [Input('dropdown-stock-list', 'value')],
)   
def update_dividend_value(value):
    return make_dash_table(TickerChart.load_dividend_history(value)),make_dash_table(TickerChart.load_stock_value(value))
    


@app.callback(
    Output(component_id='div-report', component_property='children'),
    [Input('dropdown-report', 'value')],
)   
def update_report(value):
    return make_dash_table(Report.market_top_mover(value))
    

if __name__ == "__main__":
    app.run_server(debug=True)
