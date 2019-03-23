
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
from   plotly import tools

import datetime
import json
import random
import re
import csv
import math



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
    {'label': 'DESC File',      'value': 'shape'},
    {'label': 'TOP Users',      'value': 'top' },
    {'label': 'TOP Answers',    'value': 'top_answer' },
    {'label': 'TOP Topics',     'value': 'top_topics' },
    {'label': 'NULL Values',    'value': 'count_nulls' },
    {'label': 'DISTR Values',   'value': 'histo' },
]


################################################################################
# 
# Helper Functions
# 
################################################################################


def MDfy(v):   
    rex = r'^ +'   # Match leading spaces
    return re.sub(rex, '', v, flags=re.M)



def desc(df, total):
    cols  = [ '{}. {}'.format(str(i+1), str(df.columns.values[i])) for i in range(len(df.columns.values))]    
    return dcc.Markdown(MDfy('''
        
        Release: {} recs
        
        File: **{}** recs x **{}** cols  
        
        {}  
    ''').format( 
    	total,
    	df.shape[0], 
    	df.shape[1],
    	'\n\n'.join(cols) 
    ))
    




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
    

def nulls_table(df):
	data = []
	for col in df.columns:
		nulls = df[df[col].isnull()].shape[0]
		ratio = round( nulls/df[col].shape[0], 2) 
		data.append( (col, nulls, ratio) )
	
	return table( pd.DataFrame(data, columns=['Attribute', 'Nulls', 'Ratio (%)']) )

	


def histogram(df, att):
    return go.Figure(
        data=[go.Histogram(
            x=list(df[att]),
            nbinsx=20,
            name=att
        )],
        layout=go.Layout(
            title=att,
            showlegend=False,
            autosize=True,
            margin=go.layout.Margin(
                l=50,
                r=50,
                b=100,
                t=100,
                pad=4,
                autoexpand=True
            ),            
        )
    )



def tab(df):
    cols  = list(df.columns.values)
    rows  = []
    for i in range(0, len(cols), 2):  
        rows.append(
            html.Div([
                dcc.Graph(className='six columns', figure=histogram(df, cols[i])),
                dcc.Graph(className='six columns', figure=histogram(df, cols[i+1]) if i+1 < len(cols) else None)
            ], className='row'),
        )
        
    return rows
        



'''
RELEASES_FILES_TABS = {

    'R1' : {
        'Votes' :   tab(RELEASES_FILES_DATAFRAMES['R1']['Votes']),
        'Badges':   tab(RELEASES_FILES_DATAFRAMES['R1']['Badges']),
        'Comments': tab(RELEASES_FILES_DATAFRAMES['R1']['Comments']),
        'Posts':    tab(RELEASES_FILES_DATAFRAMES['R1']['Posts']),
        'Users':    tab(RELEASES_FILES_DATAFRAMES['R1']['Users']),
    },

    'R2' : {
        'Votes' :   tab(RELEASES_FILES_DATAFRAMES['R2']['Votes']),
        'Badges':   tab(RELEASES_FILES_DATAFRAMES['R2']['Badges']),
        'Comments': tab(RELEASES_FILES_DATAFRAMES['R2']['Comments']),
        'Posts':    tab(RELEASES_FILES_DATAFRAMES['R2']['Posts']),
        'Users':    tab(RELEASES_FILES_DATAFRAMES['R2']['Users']),
    },

    'R3' : {
        'Votes' :   tab(RELEASES_FILES_DATAFRAMES['R3']['Votes']),
        'Badges':   tab(RELEASES_FILES_DATAFRAMES['R3']['Badges']),
        'Comments': tab(RELEASES_FILES_DATAFRAMES['R3']['Comments']),
        'Posts':    tab(RELEASES_FILES_DATAFRAMES['R3']['Posts']),
        'Users':    tab(RELEASES_FILES_DATAFRAMES['R3']['Users']),
    },

}

'''
RELEASES_FILES_TABS = {

    'R1' : {
        'Votes' :   tab(RELEASES_FILES_DATAFRAMES['R1']['Votes']),
        'Badges':   tab(RELEASES_FILES_DATAFRAMES['R1']['Badges']),
        'Comments': tab(RELEASES_FILES_DATAFRAMES['R1']['Comments']),
        'Posts':    tab(RELEASES_FILES_DATAFRAMES['R1']['Posts']),
        'Users':    tab(RELEASES_FILES_DATAFRAMES['R1']['Users']),
    },
}
#'''


MD_TEXT = {
    
    'histo': MDfy(
    ''' # Read csv file
        df = pd.read_csv('VOTES_jan-01-02_2018.csv')
        
        # Create histogram for each column
        for col in df.columns:
        	Histogram( df[col] )'''
    ),
    
    
    'nulls': MDfy(
    ''' # Read csv file
        df   = pd.read_csv('POSTS_jan-01-02_2018.csv')
        data = []
        
        # Compute NULLs and NULLs ratio for each dataframe' column  
        for col in df.columns:
        	sel   = df[col].isnull()         # Identify NULLs
        	nulls = df[sel].shape[0]         # Count NULLs
        	ratio = nulls/df[col].shape[0]   # NULLs / column size
        	data.append( (col, nulls, ratio) )

        Table( pd.DataFrame(data) )'''	
    ),
    
    
    'top_topics': MDfy(
    '''# Read csv file
       df = pd.read_csv('POSTS_jan-01-02_2018.csv')
       
       # Select relevant columns
       df = df[ ['Tags', 'ViewCount'] ]
       
       # Group and aggregate
       df = df.groupby('Tags').sum()
       
       Table(df)'''	
    ),
    
    
    'top_answer': MDfy(
    '''# Read csv files
       df1 = pd.read_csv('VOTES_jan-01-02_2018.csv')
       df2 = pd.read_csv('COMMENTS_jan-01-02_2018.csv')
       
       # Join VOTES and COMMENTS belonging to the same POST ('PostId')
       df3 = pd.merge(df1, df2, on='PostId')
       
       # Group and count 
       df = df.groupby('PostId').size()
       
       Table(df)'''	
    ),    
 
 
     'top_user': MDfy(
    '''# Read csv files
       df = pd.read_csv('USERS_jan-01-02_2018.csv')
       
       # Select relevant fields
       df = df[['Id','Reputation','Views','UpVotes','DownVotes','DisplayName']]
       
       # Sort 
       df = df.sort_values(by='Reputation')
       
       Table(df)'''	
    ),    
     
 
      'desc': MDfy(
    '''# Read csv files
       df = pd.read_csv('USERS_jan-01-02_2018.csv')
       
       # Num records x columns
       df.shape[0], df.shape[1]
       
       # Columns names
       list(df.columns.values)'''	
    ),   
        
    
}
        
    



################################################################################
# 
# DASH APP
# 
################################################################################

from app import app

layout = html.Div([
    
    dcc.Markdown('# Exploring Stackoverflow Releases'),
    html.Div([ 
        dcc.Markdown(''),
    ], style={'margin-bottom': '30'}),
    
    html.Div([

        html.Div(className='three columns', children=[
            dcc.Markdown('**Release**'),
            dcc.RadioItems(id='release', options=RELEASES_OPTIONS, value='R1', style={'margin-bottom': '20'}),
            dcc.Markdown('**Analytics Pipelines**'),
            dcc.RadioItems(id='operation', options=OPERATIONS_OPTIONS, value='shape'), 
        ]),
        
        html.Div(className='nine columns', children=[
            html.Div(id='output-raw',      children='[]', ),
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
        
        total = 0
        for k, df in RELEASES_FILES_DATAFRAMES[release].items():
            total += df.shape[0]
        
        return html.Div([
            dcc.Markdown('**Code Behind**'),
            dcc.Textarea(value=MD_TEXT['desc'], style={'width': '100%', 'height':50}),
            dcc.Tabs(id="tabs", children=[
                dcc.Tab(label='Votes',    children=desc(RELEASES_FILES_DATAFRAMES[release]['Votes'], total)),
                dcc.Tab(label='Badges',   children=desc(RELEASES_FILES_DATAFRAMES[release]['Badges'], total)),
                dcc.Tab(label='Comments', children=desc(RELEASES_FILES_DATAFRAMES[release]['Comments'], total)),
                dcc.Tab(label='Posts',    children=desc(RELEASES_FILES_DATAFRAMES[release]['Posts'], total)),
                dcc.Tab(label='Users',    children=desc(RELEASES_FILES_DATAFRAMES[release]['Users'], total)),
            ])
        ])
        
    
    if operation == 'top':
        df = RELEASES_FILES_DATAFRAMES[release]['Users']
        df = df[['Id','Reputation','Views','UpVotes','DownVotes','DisplayName']]
        df = df.sort_values(by='Reputation', ascending=False)
        
        return html.Div(children=[
			dcc.Markdown('**Code Behind**'),
            dcc.Textarea(value=MD_TEXT['top_user'], style={'width': '100%', 'height':50}),               
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
			dcc.Markdown('**Code Behind**'),
            dcc.Textarea(value=MD_TEXT['top_answer'], style={'width': '100%', 'height':50}),         
            table(df3)        
        ])
        
     
    if operation == 'top_topics':
        df = RELEASES_FILES_DATAFRAMES[release]['Posts']
        df = df[['Tags', 'ViewCount']].groupby('Tags').sum()
        df['Tags'] = df.index.values
        df = df.sort_values(by='ViewCount', ascending=False)
        return html.Div(children=[
            dcc.Markdown('**Code Behind**'),
            dcc.Textarea(value=MD_TEXT['top_topics'], style={'width': '100%', 'height':50}),
            table(df) 
        ])
    
    
    
    if operation == 'count_nulls':
        return html.Div([
            dcc.Markdown('**Code Behind**'),
            dcc.Textarea(value=MD_TEXT['nulls'], style={'width': '100%', 'height':50}),
            dcc.Tabs(id="tabs", children=[
                dcc.Tab(label='Votes',    children=nulls_table(RELEASES_FILES_DATAFRAMES[release]['Votes'])),
                dcc.Tab(label='Badges',   children=nulls_table(RELEASES_FILES_DATAFRAMES[release]['Badges'])),
                dcc.Tab(label='Comments', children=nulls_table(RELEASES_FILES_DATAFRAMES[release]['Comments'])),
                dcc.Tab(label='Posts',    children=nulls_table(RELEASES_FILES_DATAFRAMES[release]['Posts'])),
                dcc.Tab(label='Users',    children=nulls_table(RELEASES_FILES_DATAFRAMES[release]['Users'])),
            ])
        ])
            
            


    if operation == 'histo':
        return html.Div([
            dcc.Markdown('**Code Behind**'),
            dcc.Textarea(value=MD_TEXT['histo'], style={'width': '100%', 'height':50}),
            dcc.Tabs(id="tabs", children=[
                dcc.Tab(label='Votes',    children=RELEASES_FILES_TABS[release]['Votes']),
                dcc.Tab(label='Badges',   children=RELEASES_FILES_TABS[release]['Badges']),
                dcc.Tab(label='Comments', children=RELEASES_FILES_TABS[release]['Comments']),
                dcc.Tab(label='Posts',    children=RELEASES_FILES_TABS[release]['Posts']),
                dcc.Tab(label='Users',    children=RELEASES_FILES_TABS[release]['Users']),
            ])
        ])

 
    
    return 'xxx'



