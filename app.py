# Dash app
import dash  # use Dash version 1.16.0 or higher for this app to work
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import pendulum
from dash import dash_table
from dash.exceptions import PreventUpdate


def get_current_time():
    # get current time rounded to 5 minutes (down)
    now = pendulum.now(tz='Asia/Ho_Chi_Minh')
    now = now.start_of('minute').subtract(minutes=now.minute % 5)
    return now


def get_price_data():
    df_price = pd.read_csv('/home/ubuntu/Desktop/hello-world/crypto-twitter-trend/price.csv',
                           names=['symbol', 'price', 'create_at'])
    df_price['create_at'] = pd.to_datetime(df_price['create_at'])
    # df_price['symbol'] = df_price['symbol'].astype(str)
    return df_price


def get_tweet_data():
    df_tweet = pd.read_csv('/home/ubuntu/Desktop/hello-world/crypto-twitter-trend/result.csv',
                           names=['symbol', 'trend_point', 'sentiment_point', 'create_at'])
    df_tweet['create_at'] = pd.to_datetime(df_tweet['create_at'])
    # df_tweet['symbol'] = df_tweet['symbol'].astype(str)
    return df_tweet


now = get_current_time()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(title="Crypto Twitter Trend", external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Interval(
        id='my_interval',
        disabled=False,  # if True, the counter will no longer update
        interval=5 * 60 * 1000,  # increment the counter n_intervals every interval milliseconds
        n_intervals=0,  # number of times the interval has passed
        max_intervals=-1  # number of times the interval will be fired.
        # if -1, then the interval has no limit (the default)
        # and if 0 then the interval stops running.
    ),
    html.Br(),
    html.Div([
        dcc.Graph(
            id='crypto-trend',
            className='seven columns'
        ),
        html.Div(
            id='div-sentiment-table',
            className='four columns',
            children=[
                html.Br(),
                html.H5('Sentiment Point'),
                html.P(
                    """Positive: +1 | Neutral: 0 | Negative: -1""",
                ),
                dash_table.DataTable(
                    id='sentiment-table',
                    columns=[{'id': 'symbol', 'name': 'Symbol'}, {'id': 'sentiment_point', 'name': 'Sentiment Point'}],
                    style_cell={'textAlign': 'center'}
                    # style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'}
                )
            ]
        )

    ]),
    dcc.Dropdown(
        id='dropdown-1',
        value='BTC',
        multi=False,
        options=[
            {'label': 'BTC', 'value': 'BTC'},
            {'label': 'ETH', 'value': 'ETH'},
            {'label': 'BNB', 'value': 'BNB'},
            {'label': 'ADA', 'value': 'ADA'},
            {'label': 'XRP', 'value': 'XRP'}
        ],
        placeholder='Select a symbol'
    ),
    html.Div([
        dcc.Graph(
            id='crypto-price'
        ),
        dcc.Graph(
            id='crypto-trend-point'
        ),
        dcc.Graph(
            id='crypto-sentiment-point'
        )
    ])
])


@app.callback(
    [Output('sentiment-table', 'data'),
     Output('crypto-trend', 'figure'),
     Output('dropdown-1', 'value')],
    [Input('my_interval', 'n_intervals')]
)
def update_graph(num):
    # bar chart
    df_tweet = get_tweet_data()
    now = get_current_time()
    df_tweet_now = df_tweet[df_tweet['create_at'] == now]
    fig = px.bar(
        data_frame=df_tweet_now,
        x='trend_point',
        y='symbol',
        orientation='h',
        title=f'Top trending crypto in last 5 minutes (since {(now - pendulum.duration(minutes=5)).format("HH:mm DD/MM/YYYY")})',
    ).update_layout(yaxis={'categoryorder': 'total ascending'})

    # sentiment table
    data = df_tweet_now[['symbol', 'sentiment_point']].to_dict('records')

    # time series chart (price)
    df_price = get_price_data()

    return (data, fig, 'BTC')


@app.callback(
    [Output(component_id='crypto-price', component_property='figure'),
     Output(component_id='crypto-trend-point', component_property='figure'),
     Output(component_id='crypto-sentiment-point', component_property='figure')],
    Input(component_id='dropdown-1', component_property='value'),
)
def update_graph_2(symbol_chosen):
    df_price = get_price_data()
    df_price_symbol = df_price[df_price['symbol'] == symbol_chosen]
    fig = px.line(
        data_frame=df_price_symbol,
        x='create_at',
        y='price',
        title=f'Price of {symbol_chosen}',
        width=1900,
        height=400
    )

    df_tweet = get_tweet_data()
    df_tweet_symbol = df_tweet[df_tweet['symbol'] == symbol_chosen]
    fig2 = px.line(
        data_frame=df_tweet_symbol,
        x='create_at',
        y='trend_point',
        title=f'Trend Point of {symbol_chosen}',
        width=1900,
        height=400
    )

    fig3 = px.bar(
        data_frame=df_tweet_symbol,
        x='create_at',
        y='sentiment_point',
        title=f'Sentiment Point of {symbol_chosen}',
        width=1900,
        height=400
    )

    return (fig, fig2, fig3)


if __name__ == '__main__':
    app.run_server(debug=True)
