
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
    {'label': 'schema_atts()',         'value': 'schema'},
    {'label': 'count_null_values()',   'value': 'nulls' },
    {'label': 'count_records()',   'value': 'count' },
    {'label': 'atts_stats()',     'value': 'stats' },
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





################################################################################
# 
# Helper Functions
# 
################################################################################


def viewFile(name): 
    for rf in RELEASES_FILES:
        if rf.lower() in name.lower():
            return rf



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
        style_as_list_view=True,
        style_cell_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }],
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
        #style_table={
        #    'maxHeight': '400',
        #    'overflowY': 'scroll'
        #},          
    )
    
 



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
            dcc.Markdown('**Operations**'),
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
            output.append( dcc.Markdown('**{}**'.format(files[i])) )
            output.append( table(pd.DataFrame(schemas[i], columns=['Attribute', 'Type']))  )
            output.append( 
                html.Div([ 
                    dcc.Markdown('##'),
                ], style={'margin-bottom': '30'}),
            )
            

        return output


    # Nulls view
    if operation == 'nulls':
        v = [sum(desc['nullValue']) for desc in VIEWS[release]['attributeDescList']],
        l = [viewFile(desc['name']) for desc in VIEWS[release]['attributeDescList']]
        return dcc.Graph(figure=bar(v[0], l))


    # Count records
    if operation == 'count':
        v = [         desc['count'] for desc in VIEWS[release]['attributeDescList']]
        l = [viewFile(desc['name']) for desc in VIEWS[release]['attributeDescList']]
        return dcc.Graph(figure=bar(v, l))

    
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
        
            output.append( dcc.Markdown('**{}**'.format(obj['name'][i])) )

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
            
            output.append( table(pd.DataFrame(obj2)) )

            output.append( 
                html.Div([ 
                    dcc.Markdown('##'),
                ], style={'margin-bottom': '30'}),
            )
          
        return output


    return []




