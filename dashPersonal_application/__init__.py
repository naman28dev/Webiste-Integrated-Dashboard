import sqlite3 as sql
import os
import csv
from flask import Flask, render_template, request, redirect
from sqlite3 import Error
from turtle import goto
import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from textblob import TextBlob
import plotly.io as plt_io



def create(flask_app):

    app1 = dash.Dash(server= flask_app, title="Netflix Dashboard",url_base_pathname='/personal/')
    conn = sql.connect('naman1.db', isolation_level=None, detect_types=sql.PARSE_COLNAMES)
    db_df = pd.read_sql_query("SELECT * FROM netflix", conn)
    db_df.to_csv('netflix_dataset.csv', index=False)
    netflix_df = pd.read_csv("D:/flask1/netflix_dataset.csv")
    def clean_netflix_df(df):
        df['Country'] = df['Country'].fillna(df['Country'].mode()[0])
        df['Cast'].replace(np.nan, 'No Data', inplace=True)
        df['Director'].replace(np.nan, 'No Data', inplace=True)
        df.dropna(inplace=True)

        df.drop_duplicates(inplace=True)

        df["Date_Added"] = pd.to_datetime(df['Date_Added'])
        df['month_added'] = df['Date_Added'].dt.month
        df['month_name_added'] = df['Date_Added'].dt.month_name()
        df['year_added'] = df['Date_Added'].dt.year

        df['first_Country'] = df['Country'].apply(lambda x: x.split(",")[0])
        df['first_Country'].replace('United States', 'USA', inplace=True)
        df['first_Country'].replace('United Kingdom', 'UK', inplace=True)
        df['first_Country'].replace('South Korea', 'S. Korea', inplace=True)

        netflix_df['count'] = 1
        df['genre'] = df['Listed_In'].apply(lambda x: x.replace(' ,', ',').replace(', ', ',').split(','))
        return df
    netflix_df = clean_netflix_df(netflix_df)

    def fig_bar_horiz():
        country_order = netflix_df['first_Country'].value_counts()[:11].index
        data_q2q3 = netflix_df[['Type', 'first_Country']].groupby('first_Country')['Type'].value_counts().unstack().loc[
            country_order]
        data_q2q3['sum'] = data_q2q3.sum(axis=1)
        data_q2q3_ratio = (data_q2q3.T / data_q2q3['sum']).T[['Movie', 'TV Show']].sort_values(by='Movie', ascending=False)[
                        ::-1]
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            y=data_q2q3_ratio.index,
            x=round(data_q2q3_ratio['Movie'] * 100, 2),
            name='Movies',
            orientation='h',

            marker=dict(
                color='#34495E',
                line=dict( width=3),
            )
        ))
        fig_bar.add_trace(go.Bar(
            y=data_q2q3_ratio.index,
            x=round(data_q2q3_ratio['TV Show'] * 100, 2),
            name='TV Shows',
            orientation='h',
            marker=dict(
                color='#45B39D',
                line=dict(width=3)
            )
        ))

        fig_bar.update_layout(barmode='stack',
                            title={
                                'text': "Top 10 countries Movie & TV Show split",
                                'y': 0.9,
                                'x': 0.5,
                                'xanchor': 'center',
                                'yanchor': 'top'}
                            )
        return fig_bar

    def fig_bar_stacked():
        order = pd.DataFrame(netflix_df.groupby('Rating')['count'].sum().sort_values(ascending=False).reset_index())
        rating_order = list(order['Rating'])
        mf = netflix_df.groupby('Type')['Rating'].value_counts().unstack().sort_index().fillna(0).astype(int)[rating_order]

        movie = mf.loc['Movie']
        tv = - mf.loc['TV Show']

        fig_stacked = go.Figure()
        fig_stacked.add_trace(go.Bar(x=movie.index, y=movie, name='Movies',marker_color='#F1C40F'))
        fig_stacked.add_trace(go.Bar(x=tv.index, y=tv, name='TVShows',marker_color='#D35400'))
        fig_stacked.update_layout(barmode='relative',
                                title={
                                        'text': 'Rating distribution by Movie & TV Show',
                                        'y': 0.9,
                                        'x': 0.5,
                                        'xanchor': 'center',
                                        'yanchor': 'top'}
                                )
        return fig_stacked

    def fig_stack_without_flying():
        dfx = netflix_df[['Release_Year', 'Description']]
        dfx = dfx.rename(columns={'Release_Year': 'Release Year'})
        for index, row in dfx.iterrows():
            z = row['Description']
            testimonial = TextBlob(z)
            p = testimonial.sentiment.polarity
            if p == 0:
                sent = 'Normal'
            elif p > 0:
                sent = 'Positive'
            else:
                sent = 'Negative'
            dfx.loc[[index, 1], 'Sentiment'] = sent

        dfx = dfx.groupby(['Release Year', 'Sentiment']).size().reset_index(name='Total Content')

        dfx = dfx[dfx['Release Year'] >= 2010]
        fig_stacked_without_fly = px.bar(dfx, x="Release Year", y="Total Content",color='Sentiment')
        fig_stacked_without_fly.update_layout(title={
            'text': 'Sentiment Analysis over years for Movies and Tv Shows',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
        return fig_stacked_without_fly

    def fig_pie_purst():
        fig_purst = px.sunburst(netflix_df[netflix_df['year_added'] >= 2018], path=['year_added', 'month_name_added'],
                                values='count', color_continuous_scale='armyrose')
        fig_purst.update_layout(title={
            'text': 'Number of Movies and Tv shows added per month last 5 year',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
        return fig_purst

    def world_map():
        df_country_year = netflix_df.groupby(by=['Country','Type','Rating']).count().reset_index()
        df_country_year['total']=df_country_year.groupby(by=['Country'])['Title'].cumsum()

        fig_world_map=px.choropleth(df_country_year.sort_values(by='Rating'), locations='Country', title='Country wise statistics of Ratings',color='total', locationmode='country names', animation_frame='Rating', range_color=[0,1000], )
        return fig_world_map

    app1.layout = html.Div(children=[

        html.H1(id='header', children=[html.Div("Netflix Title Analysis", id='header-text')],
                style={'textAlign': 'center', 'color': '#b20710'}, className="mb-3"),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Div(children=[
            html.Div(children=[
                html.Div([
                    dcc.Graph(id='bar_fig', figure=fig_bar_horiz())], id='FigBarGraphDiv')
            ], className="col-md-6"),

        ], className="row"),
        html.Div(children=[
            html.Div(children=[
                html.Div([
                    dcc.Graph(id='stack_fig', figure=fig_bar_stacked())], id='StackedGraphDiv')

            ], className="col-md-6"),
            html.Div(children=[
                html.Div([
                    dcc.Graph(id='SentBarGraphDiv', figure=fig_stack_without_flying()), ])
            ], className="col-md-6"),

            ], className="col-md-6"),
            html.Div(children=[
                html.Div(children=[
                    html.Div([
                    dcc.Graph(id='world_fig', figure=world_map())], id='World_Fig')
            ], className="col-md-6"), 

            ], className="row"),

        html.Div(children=[
            html.Div(children=[
                html.Div([
                    dcc.Graph(id='purst_fig', figure=fig_pie_purst())],
                    id='PurstGraphDiv')
        

        
            ], className="col-md-6"),
            html.Div(children=[
                html.Label('Movie Statistics Calculator', id='calculator'),
                html.Div([
                    dcc.Dropdown(id='dropDown', options=[{'label': x, 'value': x} for x in netflix_df['first_Country'].unique()],
                                value='Egypt'),
                    html.Br(),
                    html.Br(),
                    html.Table([
                        html.Tbody([
                            html.Tr([
                                html.Td("No. of Movies till date"),

                                html.Td([
                                    html.Div(
                                        id="val1"

                                    )

                                ])
                            ]),
                            html.Tr([
                                html.Td("No. of TV Shows till date"),

                                html.Td([
                                    html.Div(
                                        id="val2"

                                    )

                                ])
                            ]),
                            html.Tr([
                                html.Td("Top Actor"),

                                html.Td([
                                    html.Div(
                                        id="val3"

                                    )

                                ])
                            ]),
                            html.Tr([
                                html.Td("Top Director"),

                                html.Td([
                                    html.Div(
                                        id="val4"

                                    )

                                ])
                            ])

                        ])
                    ], className="table table-striped")
                ])
            ], className="col-md-6"),

        ], className="row"),

    ], className="container-fluid",)


    @app1.callback(
        [Output('val1', 'children'), Output('val2', 'children'), Output('val3', 'children'), Output('val4', 'children')],
        Input('dropDown', 'value')
    )
    def updateTable(dropDown):
        dfx = netflix_df[['Type', 'Country']]
        dfMovie = dfx[dfx['Type'] == 'Movie']
        dfTV = dfx[dfx['Type'] == 'TV Show']
        dfM1 = dfMovie['Country'].str.split(',', expand=True).stack()
        dfTV1 = dfTV['Country'].str.split(',', expand=True).stack()
        dfM1 = dfM1.to_frame()
        dfTV1 = dfTV1.to_frame()
        dfM1.columns = ['Country']
        dfTV1.columns = ['Country']
        dfM2 = dfM1.groupby(['Country']).size().reset_index(name='counts')
        dfTV2 = dfTV1.groupby(['Country']).size().reset_index(name='counts')
        dfM2['Country'] = dfM2['Country'].str.strip()
        dfTV2['Country'] = dfTV2['Country'].str.strip()
        val11 = dfM2[dfM2['Country'] == dropDown]
        val22 = dfTV2[dfTV2['Country'] == dropDown]
        val11 = val11.reset_index()
        val22 = val22.reset_index()

        if val11.empty:
            val1 = 0
        else:
            val1 = val11.loc[0]['counts']

        if val22.empty:
            val2 = 0
        else:
            val2 = val22.loc[0]['counts']

        # Top Actor
        dfA = netflix_df[['Cast', 'Country']]
        dfA1 = dfA[dfA['Country'].str.contains(dropDown, case=False)]
        dfA2 = dfA1['Cast'].str.split(',', expand=True).stack()
        dfA2 = dfA2.to_frame()
        dfA2.columns = ['Cast']
        dfA3 = dfA2.groupby(['Cast']).size().reset_index(name='counts')
        dfA3 = dfA3[dfA3['Cast'] != 'No Cast Specified']
        dfA3 = dfA3.sort_values(by='counts', ascending=False)
        if dfA3.empty:
            val3 = "Actor data from this country is not available"
        else:
            val3 = dfA3.iloc[0]['Cast']
        # Top Director
        dfD = netflix_df[['Director', 'Country']]
        dfD1 = dfD[dfD['Country'].str.contains(dropDown, case=False)]
        dfD2 = dfD1['Director'].str.split(',', expand=True).stack()
        dfD2 = dfD2.to_frame()
        dfD2.columns = ['Director']
        dfD3 = dfD2.groupby(['Director']).size().reset_index(name='counts')
        dfD3 = dfD3[dfD3['Director'] != 'No Director Specified']
        dfD3 = dfD3.sort_values(by='counts', ascending=False)
        if dfD3.empty:
            val4 = "Director data from this country is not available"
        else:
            val4 = dfD3.iloc[0]['Director']
        return val1, val2, val3, val4

    @app1.callback(Output('line_chart', 'figure'),
                [Input('slider_year', 'value')])
    def update_graph(slider_year):
        type_movie = netflix_df[(netflix_df['Type'] == 'Movie')][['Type', 'Release_Year']]
        type_movie['type1'] = type_movie['Type']
        type_movie_1 = type_movie.groupby(['Release_Year', 'type1'])['Type'].count().reset_index()
        filter_movie = type_movie_1[(type_movie_1['Release_Year'] >= slider_year)]

        type_tvshow = netflix_df[(netflix_df['type'] == 'TV Show')][['Type', 'Release_Year']]
        type_tvshow['type2'] = type_tvshow['Type']
        type_tvshow_1 = type_tvshow.groupby(['Release_Year', 'type2'])['Type'].count().reset_index()
        filter_tvshow = type_tvshow_1[(type_tvshow_1['Release_Year'] >= slider_year)]

        return {
            'data': [go.Scatter(
                x=filter_movie['Release_Year'],
                y=filter_movie['Type'],
                mode='markers+lines',
                name='Movie',
                line=dict(shape="spline", smoothing=1.3, width=3, color='#b20710'),
                marker=dict(size=10, symbol='circle', color='#f5f5f1',
                            line=dict(color='blue', width=2)
                            ),

                hoverinfo='text',
                hovertext=
                '<b>Release Year</b>: ' + filter_movie['Release_Year'].astype(str) + '<br>' +
                '<b>Type</b>: ' + filter_movie['type1'].astype(str) + '<br>' +
                '<b>Count</b>: ' + [f'{x:,.0f}' for x in filter_movie['Type']] + '<br>'
            ),

                go.Scatter(
                    x=filter_tvshow['Release_Year'],
                    y=filter_tvshow['Type'],
                    mode='markers+lines',
                    name='TV Show',
                    line=dict(shape="spline", smoothing=1.3, width=3,color='#221f1f' ),
                    marker=dict(size=10, symbol='circle',color='#f5f5f1',
                                line=dict(color='blue',width=2)
                                ),

                    hoverinfo='text',
                    hovertext=
                    '<b>Release Year</b>: ' + filter_tvshow['Release_Year'].astype(str) + '<br>' +
                    '<b>Type</b>: ' + filter_tvshow['type2'].astype(str) + '<br>' +
                    '<b>Count</b>: ' + [f'{x:,.0f}' for x in filter_tvshow['Type']] + '<br>'

                )],
            'layout': go.Layout(
                title={
                    'text': 'Movies and TV Shows by Release Year',
                    'xanchor': 'right',
                    'yanchor': 'top'},
                width=1200
            ),

        }
    return app1
