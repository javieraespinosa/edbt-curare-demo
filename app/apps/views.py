
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


import curare_releaseView as cr_View


################################################################################
# 
# CONSTANTS
# 
################################################################################


RELEASES_FILES = [
    'Votes',
    'Posts',
    'Comments',
    'Badges',
    'Users'
]


RELEASES_OPTIONS = [
    {'label': 'January 1rst 2018',  'value': 'R1'},
    {'label': 'January 2nd 2018',   'value': 'R2'},
    {'label': 'January 3rd 2018',   'value': 'R3'}
]


OPERATIONS_OPTIONS = [
    {'label': 'VIEW["SCHEMA"]',  'value': 'schema'},
    {'label': 'VIEW["COUNT"]',   'value': 'count' },
    {'label': 'VIEW["NULLS"]',   'value': 'nulls' },
    {'label': 'VIEW["STATS" ]',  'value': 'stats' },    
    {'label': 'VIEW["DISTR"]',   'value': 'histo' },
    
]



VIEWS = {
    'R1': json.load(open('./data/views/R1.json')), 
    'R2': json.load(open('./data/views/R2.json')),
    'R3': json.load(open('./data/views/R3.json')),
}


VIEWS_NULLS = {
    'R1': [sum(i['nullValue']) for i in VIEWS['R1']['attributeDescList']],
    'R2': [sum(i['nullValue']) for i in VIEWS['R2']['attributeDescList']],
    'R3': [sum(i['nullValue']) for i in VIEWS['R3']['attributeDescList']],
}


VIEWS_SCHEMAS = {
    'R1': cr_View.getReleaseViewSchemata(VIEWS['R1'], RELEASES_FILES),
    'R2': cr_View.getReleaseViewSchemata(VIEWS['R2'], RELEASES_FILES),
    'R3': cr_View.getReleaseViewSchemata(VIEWS['R3'], RELEASES_FILES),
}


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





################################################################################
# 
# Helper Functions
# 
################################################################################


def viewFile(name): 
    for rf in RELEASES_FILES:
        if rf.lower() in name.lower():
            return rf



def release_stats(release):

    obj = {
        'name'   : [viewFile(desc['name']) for desc in VIEWS[release]['attributeDescList']],
        'min'    : [desc['minValue'] for desc in VIEWS[release]['attributeDescList']],
        'max'    : [desc['maxValue'] for desc in VIEWS[release]['attributeDescList']],
        'median' : [desc['median']   for desc in VIEWS[release]['attributeDescList']],
        'mean'   : [desc['mean']     for desc in VIEWS[release]['attributeDescList']],            
        'nulls'  : [desc['nullValue']for desc in VIEWS[release]['attributeDescList']],
    }
    
    stats = {}
    for i in range(len(obj['name'])):
    
        file_atts=[]
        for att_schema in VIEWS_SCHEMAS[release][i][1]: 
            for v in att_schema.values():
                file_atts.append(v)       
                        
        obj2 = {
            'Attribute' : [att[0] for att in file_atts],
            'min'    : obj['min'][i],
            'max'    : obj['max'][i],
            'median' : obj['median'][i],
            'mean'   : obj['mean'][i],
            'nulls'  : obj['nulls'][i]
        }
        
        df       = pd.DataFrame(obj2)
        df.index = df['Attribute'] 
        
        stats[obj['name'][i]] = df.drop(['Attribute'], axis=1)
    
    return stats



################################################################################
# 
# PLOTLY FIGURES
# 
################################################################################


def bar(values, labels):
    
    return go.Figure(
        data=[
            go.Bar(
                x=labels,
                y=values,
                text=values,
                textposition='auto',
            ),
        ],
        layout=go.Layout(
            showlegend=False,
        )
    )



def table(df):  
    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows"),
        style_cell={'textAlign': 'left'},
        style_filter={'textAlign': 'left'},
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
        filtering=True,
    )
    
 



def histogram(df, att, stats=None):
    
    data = [
        go.Histogram(
            x=list(df[att]),
            nbinsx=20,
            name=att
        ),        
    ]
    
    return go.Figure(
        data=data,
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



def tab(df, stats=None):
    
    cols  = list(df.columns.values)
    rows  = []
        
    for i in range(0, len(cols), 2):
        
        md1 = ''
        md2 = ''
        
        if stats is not None:
            md1 = 'MIN: {}\n\n  MAX: {}\n\n  MEDIAN: {}\n\n  MEAN: {}'.format(
                stats.loc[cols[i]]['min'],
                stats.loc[cols[i]]['max'],
                stats.loc[cols[i]]['median'],
                stats.loc[cols[i]]['mean']
            )
            
            md2 = 'MIN: {}\n\n  MAX: {}\n\n  MEDIAN: {}\n\n  MEAN: {}'.format(
                stats.loc[cols[i+1]]['min'],
                stats.loc[cols[i+1]]['max'],
                stats.loc[cols[i+1]]['median'],
                stats.loc[cols[i+1]]['mean']
            )
            

        rows.append(
            html.Div([
                html.Div([
                    dcc.Graph(figure=histogram(df, cols[i] )),
                    #dcc.Markdown(md1)    
                ], className='six columns'),
                
                html.Div([
                    dcc.Graph(figure=histogram(df, cols[i+1]) if i+1 < len(cols) else None),
                    #dcc.Markdown(md2)    
                ], className='six columns'),
            ], className='row'),
        )
        
        #break        
        
    return rows
        

#'''
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

#'''


RELEASES_STATS = {
    'R1': release_stats('R1'),
    'R2': release_stats('R2'),
    'R3': release_stats('R3'),
}

'''
RELEASES_FILES_TABS = {

    'R1' : {
        'Votes' :   tab(RELEASES_FILES_DATAFRAMES['R1']['Votes'],    RELEASES_STATS['R1']['Votes']),
        'Badges':   tab(RELEASES_FILES_DATAFRAMES['R1']['Badges'],   RELEASES_STATS['R1']['Badges']),
        'Comments': tab(RELEASES_FILES_DATAFRAMES['R1']['Comments'], RELEASES_STATS['R1']['Comments']),
        'Posts':    tab(RELEASES_FILES_DATAFRAMES['R1']['Posts'],    RELEASES_STATS['R1']['Posts']),
        'Users':    tab(RELEASES_FILES_DATAFRAMES['R1']['Users'],    RELEASES_STATS['R1']['Users']),
    },
}
'''



################################################################################
# 
# DASH APP
# 
################################################################################

from app import app

layout = html.Div([
    
    dcc.Markdown('# **CURARE VIEWS** in Action'),
    html.Div([ 
        dcc.Markdown('## Exploring Stackoverflow Releases'),
    ], style={'margin-bottom': '30'}),
    
    html.Div([

        html.Div(className='three columns', children=[
            dcc.Markdown('**Release**'),
            dcc.RadioItems(id='release', options=RELEASES_OPTIONS, value='R1', style={'margin-bottom': '20'}),
            dcc.Markdown('**Views Attributes**'),
            dcc.RadioItems(id='operation', options=OPERATIONS_OPTIONS, value='schema'), 
        ]),
        
        html.Div(className='nine columns', children=[
            html.Div(id='output',    children='[]', ),
        ]),
    
    ], className='row')
    
], className='container')





################################################################################
# 
# DASH CALLBACKS
# 
################################################################################


@app.callback(
    Output(component_id='output',     component_property='children'),
    [Input(component_id='operation',  component_property='value'),
     Input(component_id='release',    component_property='value')],
)
def onOperationSelected(operation, release):

    # Schema
    if operation == 'schema':
                
        files   = []
        schemas = []
        
        for i in range(len(VIEWS_SCHEMAS[release])):
            
            file_schema = VIEWS_SCHEMAS[release][i]            
            file_name = file_schema[0]
            file_atts = []
            
            for att_schema in file_schema[1]:                
                for v in att_schema.values():
                    file_atts.append(v)
                           
            files.append  (file_name)
            schemas.append(file_atts)
        
        output = []
        for i in range(len(files)):
            output.append( 
                dcc.Tab(
                    label=files[i],
                    children=table(
                        pd.DataFrame(schemas[i], columns=['Attribute', 'Type'])
                    )  
                )
            )
        
        return dcc.Tabs(id="tabs", children=output)




    # Nulls view
    if operation == 'nulls':
        v = [sum(desc['nullValue']) for desc in VIEWS[release]['attributeDescList']],
        l = [viewFile(desc['name']) for desc in VIEWS[release]['attributeDescList']]
        v = v[0]
        
        v = []
        l = RELEASES_FILES
        for f in RELEASES_FILES:
            df = RELEASES_FILES_DATAFRAMES[release][f]
            x  = 0
            for col in df.columns:
                x += df[df[col].isnull()].shape[0]
            
            v.append(x)
        
        s = 'Total Number of NULLs: ' + str( sum(v) )
        
        return html.Div(children=[
            dcc.Graph(figure=bar(v, l)),
            html.Div(dcc.Markdown(s), style={'text-align': 'center'}),
        ])
        
 

    # Count records
    if operation == 'count':
        v = [         desc['count'] for desc in VIEWS[release]['attributeDescList']]
        l = [viewFile(desc['name']) for desc in VIEWS[release]['attributeDescList']]
        
        v = []
        l = RELEASES_FILES
        for f in RELEASES_FILES:
            v.append( RELEASES_FILES_DATAFRAMES[release][f].shape[0] )
        
        s = 'Total Number of Records: ' + str(sum(v))
        
        return html.Div(children=[
            dcc.Graph(figure=bar(v, l)),
            html.Div( dcc.Markdown(s) , style={'text-align': 'center'}),   
        ])
        
        


    if operation == 'stats':

        obj = {
            'name'   : [viewFile(desc['name']) for desc in VIEWS[release]['attributeDescList']],
            'min'    : [desc['minValue'] for desc in VIEWS[release]['attributeDescList']],
            'max'    : [desc['maxValue'] for desc in VIEWS[release]['attributeDescList']],
            'median' : [desc['median']   for desc in VIEWS[release]['attributeDescList']],
            'mean'   : [desc['mean']     for desc in VIEWS[release]['attributeDescList']],            
            'nulls'  : [desc['nullValue']for desc in VIEWS[release]['attributeDescList']],
        }
        
        output = []
        for i in range(len(obj['name'])):
        
            file_atts=[]
            for att_schema in VIEWS_SCHEMAS[release][i][1]: 
                for v in att_schema.values():
                    file_atts.append(v)       
                            
            obj2 = {
                'Attribute' : [att[0] for att in file_atts],
                'min'    : obj['min'][i],
                'max'    : obj['max'][i],
                'median' : obj['median'][i],
                'mean'   : obj['mean'][i],
                'nulls'  : obj['nulls'][i]
            }
            
            
            md  = '> `Filters: eq "Asia" | > num(500) | < num(80)` '
            
            output.append( 
                dcc.Tab(
                    label=obj['name'][i],
                    children=html.Div(children=[
                        dcc.Markdown(md),
                        table( pd.DataFrame(obj2) ) 
                    ])
                )
            )

        return dcc.Tabs(id="tabs", children=output)        



    if operation == 'histo':
        
        return dcc.Tabs(id="tabs", children=[
                dcc.Tab(label='Votes',    children=RELEASES_FILES_TABS[release]['Votes']),
                dcc.Tab(label='Badges',   children=RELEASES_FILES_TABS[release]['Badges']),
                dcc.Tab(label='Comments', children=RELEASES_FILES_TABS[release]['Comments']),
                dcc.Tab(label='Posts',    children=RELEASES_FILES_TABS[release]['Posts']),
                dcc.Tab(label='Users',    children=RELEASES_FILES_TABS[release]['Users']),
        ])



    return []




