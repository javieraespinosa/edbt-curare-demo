
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.dashboard_objs as dashboard

import datetime
import json
import random
import re
import csv



################################################################################
# 
# CONSTANTS
# 
################################################################################

RELEASES_FILES = [
    'Votes',
    'Badges',
    'Comments',
    'Posts',
    'Users'
]


RELEASES_FILES_DATAFRAMES = {

    'R1' : {
        'Votes' :   pd.read_csv('./data/releases/jan-01-02_2018/VOTES_jan-01-02_2018.csv'),
        'Badges':   pd.read_csv('./data/releases/jan-01-02_2018/BADGES_jan-01-02_2018.csv'),
        'Comments': pd.read_csv('./data/releases/jan-01-02_2018/COMMENTS_jan-01-02_2018.csv'),
        'Posts':    pd.read_csv('./data/releases/jan-01-02_2018/POSTS_jan-01-02_2018.csv'),
        'Users':    pd.read_csv('./data/releases/jan-01-02_2018/USERS_jan-01-02_2018.csv'),
    },
    
    'R2' : {
        'Votes' :   pd.read_csv('./data/releases/jan-02-03_2018/VOTES_jan-02-03_2018.csv'),
        'Badges':   pd.read_csv('./data/releases/jan-02-03_2018/BADGES_jan-02-03_2018.csv'),
        'Comments': pd.read_csv('./data/releases/jan-02-03_2018/COMMENTS_jan-02-03_2018.csv'),
        'Posts':    pd.read_csv('./data/releases/jan-02-03_2018/POSTS_jan-02-03_2018.csv'),
        'Users':    pd.read_csv('./data/releases/jan-02-03_2018/USERS_jan-02-03_2018.csv'),
    },
    
    'R3' : {
        'Votes' :   pd.read_csv('./data/releases/jan-03-04_2018/VOTES_jan-03-04_2018.csv'),
        'Badges':   pd.read_csv('./data/releases/jan-03-04_2018/BADGES_jan-03-04_2018.csv'),
        'Comments': pd.read_csv('./data/releases/jan-03-04_2018/COMMENTS_jan-03-04_2018.csv'),
        'Posts':    pd.read_csv('./data/releases/jan-03-04_2018/POSTS_jan-03-04_2018.csv', quoting=csv.QUOTE_NONE, error_bad_lines=False),
        'Users':    pd.read_csv('./data/releases/jan-03-04_2018/USERS_jan-03-04_2018.csv'),
    },
}


RELEASES_OPTIONS = [
    {'label': 'January 1rst 2018',  'value': 'R1'},
    {'label': 'January 2nd 2018',   'value': 'R2'},
    {'label': 'January 3rd 2018',   'value': 'R3'}
]


OPERATIONS_OPTIONS = [
    {'label': 'file_desc()',    'value': 'shape'},
    {'label': 'top_user()',     'value': 'top' },
    {'label': 'top_answer()',   'value': 'top_answer' },
    {'label': 'top_topics()',   'value': 'top_topics' },
    {'label': 'count_nulls()',  'value': 'count_nulls' },
]


################################################################################
# 
# Helper Functions
# 
################################################################################


def MDfy(v):   
    rex = r'^ +'   # Match leading spaces
    return re.sub(rex, '', v, flags=re.M)


def textArea(value):
    return dcc.Textarea(
        value=value,
        style={'width': '100%'}
    )
    


def md_file_desc(_file, df):
    
    return MDfy('''
        **{}** 
        
        {}
        
        _{} recs x {} cols_
        
    ''').format(_file, ', '.join(list(df.columns.values)), df.shape[0], df.shape[1] )
    



def md_nulls(_file, df):
        
    nulls=[]
    for col in df.columns:
        n_count = df[ df[col].isnull() ].shape[0]
        tmp = (col, n_count, n_count/df[col].shape[0])
        nulls.append(tmp)
    
    s = ''.join(['{}: {} ({}%) \n\n'.format(n[0], n[1], round(n[2], 2) ) for n in nulls])

    return MDfy('''
        **{}** 
        
        {}
        
    ''').format(_file, s)
    




################################################################################
# 
# PLOTLY FIGURES
# 
################################################################################


def table(df):  
    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows"),
        style_cell={'textAlign': 'left'},
        style_as_list_view=True,
        style_cell_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }],
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },    
        sorting=True,
        pagination_mode="fe",
        pagination_settings={
            "displayed_pages": 1,
            "current_page": 0,
            "page_size": 10,
        },        
    )
    
 



################################################################################
# 
# DASH APP
# 
################################################################################

from app import app

layout = html.Div([
    
    dcc.Markdown('# Exploring Stackoverflow Releases'),
    html.Div([ 
        dcc.Markdown('## --'),
    ], style={'margin-bottom': '30'}),
    
    html.Div([

        html.Div(className='three columns', children=[
            dcc.Markdown('**Release**'),
            dcc.RadioItems(id='release', options=RELEASES_OPTIONS, value='R1', style={'margin-bottom': '20'}),
            dcc.Markdown('**Operations**'),
            dcc.RadioItems(id='operation', options=OPERATIONS_OPTIONS, value='shape'), 
        ]),
        
        html.Div(className='nine columns', children=[
            html.Div(id='output-raw',    children='[]', ),
        ]),
    
    ], className='row')
    
], className='container')





################################################################################
# 
# DASH CALLBACKS
# 
################################################################################


@app.callback(
    Output(component_id='output-raw', component_property='children'),
    [Input(component_id='operation',  component_property='value'),
     Input(component_id='release',    component_property='value')],
)
def onOperationSelected(operation, release):
    
    if operation == 'shape':
        md = ''
        md+= md_file_desc('Votes',    RELEASES_FILES_DATAFRAMES[release]['Votes'])
        md+= md_file_desc('Badges',   RELEASES_FILES_DATAFRAMES[release]['Badges'])
        md+= md_file_desc('Comments', RELEASES_FILES_DATAFRAMES[release]['Comments'])
        md+= md_file_desc('Posts',    RELEASES_FILES_DATAFRAMES[release]['Posts'])
        md+= md_file_desc('Users',    RELEASES_FILES_DATAFRAMES[release]['Users'])    

        return html.Div(children=[
            dcc.Markdown(md),
        ])
        
    
    if operation == 'top':
        df = RELEASES_FILES_DATAFRAMES[release]['Users']
        df = df[['Id','Reputation','Views','UpVotes','DownVotes','DisplayName']]
        df = df.sort_values(by='Reputation', ascending=False)
        return html.Div(children=[
            dcc.Markdown('Projection(**USERS**) => Sort'),
            table(df)
        ])
        
    
    if operation == 'top_answer':
        df1 = RELEASES_FILES_DATAFRAMES[release]['Votes']
        df2 = RELEASES_FILES_DATAFRAMES[release]['Comments']
        df3 = pd.merge(df1, df2, on=['PostId'])
        
        df3 = df3.groupby(['PostId'])
        df3 = df3.size().reset_index(name='Counts')
        df3 = df3.sort_values(by='Counts', ascending=False)

        return html.Div(children=[
            dcc.Markdown('_Answer popularity= votes + comments_'),
            dcc.Markdown('Join(**Votes**, **Comments**, on=PostId) => GroupBy(PostId) => count(group) '),
            table(df3)        
        ])
        
     
    if operation == 'top_topics':
        df = RELEASES_FILES_DATAFRAMES[release]['Posts']
        df = df[['Tags', 'ViewCount']].groupby('Tags').sum()
        df['Tags'] = df.index.values
        df = df.sort_values(by='ViewCount', ascending=False)
        
        return html.Div(children=[      
            table(df) 
        ])
    
    
    if operation == 'count_nulls':
        md = ''
        md+= md_nulls('Votes',    RELEASES_FILES_DATAFRAMES[release]['Votes'])
        md+= md_nulls('Badges',   RELEASES_FILES_DATAFRAMES[release]['Badges'])
        md+= md_nulls('Comments', RELEASES_FILES_DATAFRAMES[release]['Comments'])
        md+= md_nulls('Posts',    RELEASES_FILES_DATAFRAMES[release]['Posts'])
        md+= md_nulls('Users',    RELEASES_FILES_DATAFRAMES[release]['Users'])    

        return html.Div(children=[
            dcc.Markdown(md),
        ])
            
        
    return 'xxx'







