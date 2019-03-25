
import pandas as pd
import dash
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


################################################################################
# 
# CONSTANTS
# 
################################################################################


POSTS_ATTRIBUTES = [
    {'label': 'Id',                     'value': 'Id'},
    {'label': 'PostTypeId',             'value': 'PostTypeId'},
    {'label': 'AcceptedAnswerId',       'value': 'AcceptedAnswerId'},
    {'label': 'ParentId',               'value': 'ParentId'},
    {'label': 'CreationDate',           'value': 'CreationDate'},  
    {'label': 'DeletionDate',           'value': 'DeletionDate'},
    {'label': 'Score',                  'value': 'Score'},
    {'label': 'ViewCount',              'value': 'ViewCount'},
    {'label': 'Body',                   'value': 'Body'},
    {'label': 'OwnerUserId',            'value': 'OwnerUserId'},
    {'label': 'OwnerDisplayName',       'value': 'OwnerDisplayName'},            
    {'label': 'LastEditorUserId',       'value': 'LastEditorUserId'},
    {'label': 'LastEditorDisplayName',  'value': 'LastEditorDisplayName'},
    {'label': 'LastEditDate',           'value': 'LastEditDate'},
    {'label': 'LastActivityDate',       'value': 'LastActivityDate'},
    {'label': 'Title',                  'value': 'Title'},
    {'label': 'Tags',                   'value': 'Tags'},
    {'label': 'AnswerCount',            'value': 'AnswerCount'},
    {'label': 'CommentCount',           'value': 'CommentCount'},
    {'label': 'FavoriteCount',          'value': 'FavoriteCount'},
    {'label': 'ClosedDate',             'value': 'ClosedDate'},                 
    {'label': 'CommunityOwnedDate',     'value': 'CommunityOwnedDate'}
 ]


BADGES_ATTRIBUTES = [
    {'label': 'Id',         'value': 'Id'}, 
    {'label': 'UserId',     'value': 'UserId'},
    {'label': 'Name',       'value': 'Name'},
    {'label': 'Date',       'value': 'Date'},
    {'label': 'Class',      'value': 'Class'},
    {'label': 'TagBased',   'value': 'TagBased'}
]

COMMENTS_ATTRIBUTES = [
    {'label': 'Id',                 'value': 'Id'},
    {'label': 'PostId',             'value': 'PostId'},
    {'label': 'Score',              'value': 'Score'},
    {'label': 'Text',               'value': 'Text'},
    {'label': 'CreationDate',       'value': 'CreationDate'},
    {'label': 'UserDisplayName',    'value': 'UserDisplayName'},
    {'label': 'UserId',             'value': 'UserId'}
]

USERS_ATTRIBUTES = [
    {'label': 'Id',                 'value': 'Id'},
    {'label': 'Reputation',         'value': 'Reputation'},
    {'label': 'CreationDate',       'value': 'CreationDate'},
    {'label': 'DisplayName',        'value': 'DisplayName'},
    {'label': 'LastAccessDate',     'value': 'LastAccessDate'},
    {'label': 'WebsiteUrl',         'value': 'WebsiteUrl'},
    {'label': 'Location',           'value': 'Location'},
    {'label': 'AboutMe',            'value': 'AboutMe'},
    {'label': 'Views',              'value': 'Views'},
    {'label': 'UpVotes',            'value': 'UpVotes'},
    {'label': 'DownVotes',          'value': 'DownVotes'},
    {'label': 'ProfileImageUrl',    'value': 'ProfileImageUrl'},
    {'label': 'EmailHash',          'value': 'EmailHash'},
    {'label': 'AccountId',          'value': 'AccountId'}
]

VOTES_ATTRIBUTES = [
    {'label': 'Id',              'value': 'Id'},
    {'label': 'PostId',          'value': 'PostId'},
    {'label': 'VoteTypeId',      'value': 'VoteTypeId'},
    {'label': 'UserId',          'value': 'UserId'},
    {'label': 'CreationDate',    'value': 'CreationDate'},
    {'label': 'BountyAmount',    'value': 'BountyAmount'},
]

Q_RELEASES_OPTIONS = [
    {'label': 'January 1rst 2018',  'value': 'R1'},
    {'label': 'January 2nd 2018',   'value': 'R2'},
    {'label': 'January 3rd 2018',   'value': 'R3'}
]

Q_SLIDER_MARKS = {
    0: {'label': 'Low' },
    1: {'label': 'Regular'},
    2: {'label': 'High'}
}


QUESTIONS_LABELS = [ 'Q' + str(i+1) for i in range(6) ]

QUESTIONS = [
    'Q1. Which release has the **most number of records**?',
    'Q2. Which is the release with best quality? (**fewest null values**)',
    'Q3. Which **Posts** attribute(s) help to identify the **most trendy topic** in a release?',
    'Q4. In which release **USERS.location** is most **evenly distributed**?',
    'Q5. Which attribute(s) help identify the **USERS** with the **highest reputation**?',
    'Q6. Which attributes can be used as **sharding keys** to fragment releases using an **interval based strategy**?',
]

ANSWERS  = [
    'R3',
    'R1',
    ['Score', 'FavoriteCount', 'ViewCount'],
    'R2',    
    [
        ['Id', 'Name'], 
        ['PostId', 'Score'], 
        ['Id', 'Score', 'Tags'], 
        [], 
        []
    ],
    [
        ['Name'],
        ['Id'],
        ['Id'], 
        ['Id', 'DisplayName'], 
        ['Id', 'PostId']
    ]
]


def MDfy(obj):   
    rex = r'^\s+'   # Match leading spaces
    return {k: re.sub(rex, '', v, flags=re.M) for (k, v) in obj.items()}

MD_TEXTS = MDfy({
    
    'welcome': '''
        ## The CURARE Challenge
        ### Exploring Stack Overflow datasets
        ### **Manual** vs **Views** 
    ''',
    
    'question': '''
        ### Match {}
        #### {}
    ''',
    
    'pause': '''
        ### Ready for Match 2 ?
    ''',
    
    'results': '''
        # The CURARE Challenge
    ''',
    
    'results-1': '''
        ### This is how your **SCORE** evolved over time 
        ###### Views should warranty a higher score
    ''',
    
    'results-2': '''
        ### This is how much **time** you spend **per question**
        ###### Views should help you get the job faster
    ''',    
    
    'results-3': '''
        ### And this is your **effort perception**
    ''',        
    
   'results-4': '''
        ### Views are the best thing on earth, rigth? ;)
    ''',      
    
})



################################################################################
# 
# Helper Functions
# 
################################################################################

def w_scores(scores, times):
    
    upper_limit = 180
    lower_limit = 60
    
    w = 0
    ws = [0]*len(scores)
    
    for i in range(len(scores)):
        
        # No penalty if time to answer is reasonable
        if times[i] < lower_limit:
            w = 0
        
        # Max penalty if user took too much time
        elif times[i] > upper_limit:
            w = 1
        
        # Penalty proportional to time to answer
        else:
            w = (times[i]-lower_limit)/ (upper_limit-lower_limit)
        
        # Apply penalty to score
        ws[i] = round(scores[i]-w, 2)
        ws[i] = ws[i] if ws[i] > 0 else 0

    return ws
        

def score(selection, answers):
    
    score = 0
    
    # Question with only 1 answer
    if not isinstance(answers, list):
        score = 1 if selection == answers else 0
    
    # Question with more than 1 answers
    elif not isinstance(answers[0], list):
        s=0
        for sel in selection:
            s += 1 if sel in answers else -1
        
        score = float(s)/len(answers) if s > 0 else 0
    
    # Question with multi-parts answers 
    else:
        p=0
        for i in range(len(answers)):
            s=0
                        
            for sel in selection[i]:
                s += 1 if sel in answers[i] else -1
            
            if len(answers[i])==0:
                p += 0.2 if s == 0 else 0
            
            elif s > 0:
                p += s/len(answers[i])*0.2
                            
        score = p
    
    return round(score, 2)


def INIT_Q(I):
    if I == 0:
        return 0
    if I in range(1,7):
        return I-1
    if I in range(7,15):
        return I-2


################################################################################
# 
# PLOTLY FIGURES
# 
################################################################################

def bar(name1, values1, name2, values2):

    return go.Figure(
        data=[
            go.Bar(
                x=QUESTIONS_LABELS,
                y=values1,
                text=[ str(y)+'s' for y in values1],
                textposition = 'auto',
                name=name1,
            ),
            go.Bar(
                x=QUESTIONS_LABELS,
                y=values2,
                text=[ str(y)+'s' for y in values2],
                textposition = 'auto',
                name=name2
            )
        ],
        layout=go.Layout(
            showlegend=True,
            barmode='stack'
        )
    )


def donut(text, values, legend):

    labels = ['Low','Regular','High']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    return go.Figure(
        data=[
            go.Pie(
                values=values,
                labels=labels,
                text=labels,
                hole=0.4,
                hoverinfo='none',
                marker={'colors': colors}
            ),            
        ],
        layout=go.Layout(
            showlegend=legend,
            annotations= [
                {
                    "font": { "size": 20 },
                    "showarrow": False,
                    "text": text
                }, 
            ],
        )
    )    


def stack(name1, values1, name2, values2):

    def f(vls):
        tmp=[]
        score = 6
        for v in vls:
            score -= 1-v
            tmp.append( round(score/6*100, 2) )
        return tmp
    
    return go.Figure(
       data=[
            go.Scatter(
                x=QUESTIONS_LABELS,
                y=f(values1),
                fill='tozeroy',
                name=name1,
                mode='lines',
            ),
            go.Scatter(
                x=QUESTIONS_LABELS,
                y=f(values2),
                fill='tonexty',
                name=name2,
                mode='lines'
            ),    
        ],
        layout=go.Layout(
            showlegend=True,            
        )
    )    



################################################################################
# 
# DASH LAYOUTS
# 
################################################################################

def divs(ids):
    return [html.Div(id=_id, children=[]) for _id in ids]
    

def message(txt, button_label):
    return [
        dcc.Markdown(txt),
        html.Button(id='button', children=button_label, className='button-primary'),
    ] + divs(['q-effort', 'q-release', 'q-badges', 'q-comments', 'q-posts', 'q-users', 'q-votes'])


def q_commons():
    return [
        dcc.Slider(id='q-effort', min=0, max=2, marks=Q_SLIDER_MARKS, step=1, value=0, dots=True, className='slider'), 
        html.Button(id='button', children='Next', className='button-primary'),            
    ]


def q_release(txt):
    return [
        dcc.Markdown(txt),
        dcc.RadioItems(id='q-release', options=Q_RELEASES_OPTIONS, value=''),
    ] + q_commons() + divs(['q-badges', 'q-comments', 'q-posts', 'q-users', 'q-votes'])
    
        
def q_attributes(txt, hide):
    
    files   = ['Badges', 'Comments', 'Posts', 'Users', 'Votes']
    options = [BADGES_ATTRIBUTES, COMMENTS_ATTRIBUTES, POSTS_ATTRIBUTES, USERS_ATTRIBUTES, VOTES_ATTRIBUTES]
    
    children = []
    for i in range(len(files)):
        
        label = html.Label(files[i])
        ddown = dcc.Dropdown(
            id='q-{}'.format(files[i].lower()), 
            options=options[i],   
            value='', 
            multi=True,
        )

        children.append(
            html.Div(
                children= [ label, ddown ],
                style   = {'display': 'none'} if files[i] in hide else {'display': 'block'}
            )
        )
    
    return [
        dcc.Markdown(txt),
        html.Div(children),
    ] + q_commons() + divs(['q-release'])
    

def nextMatch():
    return [
        html.H2('Match 2?'),
        html.Button(id='button', children='Continue'),
    ] + divs(['q-effort', 'q-release', 'q-badges', 'q-comments', 'q-posts', 'q-users', 'q-votes', 'results'])
    

def results(context):
    
    times  = context['Q_TIMES']
    scores = context['Q_SCORES']
    effort = context['Q_EFFORTS']

    s  = {'margin-top': 120}
    n1 = 'Match1'
    n2 = 'Match2'
        
    ws = w_scores(scores, times)
    
    fig_scores   = stack(n1, ws[0:6],    n2, ws[6:12])
    fig_times    = bar  (n1, times[0:6], n2, times[6:12]) 
    fig_effort_1 = donut(n1, [effort[0:6].count(x)  for x in range(3)], False)
    fig_effort_2 = donut(n2, [effort[6:12].count(x) for x in range(3)], True)
    
    return [    
    
        dcc.Markdown(MD_TEXTS['results']),
        
        html.Div(className='row', children=[
            html.Div (className='four columns',  children=dcc.Markdown(MD_TEXTS['results-1']), style=s),
            dcc.Graph(className='eight columns', figure=fig_scores),
        ]),        

        html.Div(className='row', children=[
            dcc.Graph(className='eight columns', figure=fig_times),
            html.Div (className='four columns',  children=dcc.Markdown(MD_TEXTS['results-2']), style=s),
        ]),    

        html.Div(className='row', children=[
            html.Div( className='two columns',  children=dcc.Markdown(MD_TEXTS['results-3']), style=s),
            dcc.Graph(className='five columns', figure=fig_effort_1),
            dcc.Graph(className='five columns', figure=fig_effort_2),
        ]),
        
        dcc.Markdown(MD_TEXTS['results-4']),

    ]




################################################################################
# 
# DASH APP
# 
################################################################################

from app import app

layout = html.Div([
    html.Div(id='main-div', children=message('', '')),
    html.Div(id='context',  children=None,       style={'display': 'none'}),
    html.Button(id='button_end', children='End', style={'display': 'none'}),
], className='container')




################################################################################
# 
# DASH CALLBACKS
# 
################################################################################


LAYOUTS = [
    'welcome',
    'q-release',
    'q-release',
    'q-attributes',
    'q-release',
    'q-attributes',
    'q-attributes',
    'nextMatch',
    'q-release',
    'q-release',
    'q-attributes',
    'q-release',
    'q-attributes',
    'q-attributes',
    'results'
]
@app.callback(
    Output(component_id='main-div', component_property='children'),
    [Input(component_id='context',  component_property='children')],
)
def onContextUpdate(context):
    
    if context:
        context = json.loads(context)
        _type   = LAYOUTS[context['I']]

        H = ['Badges', 'Comments', 'Users', 'Votes']
        
        q = QUESTIONS[context['Q']%6]
        m = 1 if context['I'] < 7 else 2
        h = H if context['I'] in [3, 10] else [] 
            
        if _type == 'welcome':
            return message(MD_TEXTS['welcome'], 'Start')
            
        if _type == 'q-release':
            txt = MD_TEXTS['question'].format(m, q)
            return q_release(txt)
            
        if _type == 'q-attributes':
            txt = MD_TEXTS['question'].format(m, q)
            return q_attributes(txt, h)
        
        if _type == 'nextMatch':
            return message(MD_TEXTS['pause'], 'Continue')
            
        if _type == 'results':
            return results(context)
    
    else:
        return message(MD_TEXTS['welcome'], 'Start')
        


I = 0
@app.callback(
    Output(component_id='context',    component_property='children'),
    [Input(component_id='button',     component_property='n_clicks'),
     Input(component_id='button_end', component_property='n_clicks')],
    [State(component_id='button',     component_property='n_clicks_timestamp'),
     State(component_id='q-effort',   component_property='value'),
     State(component_id='q-release',  component_property='value'),
     State(component_id='q-badges',   component_property='value'),
     State(component_id='q-comments', component_property='value'),
     State(component_id='q-posts',    component_property='value'),
     State(component_id='q-users',    component_property='value'),
     State(component_id='q-votes',    component_property='value'),
     State(component_id='context',    component_property='children')]
)
def onClick(button, button_end, timestamp, q_effort, q_release, q_badges, q_comments, q_posts, q_users, q_votes, context,):

    context = json.loads(context) if context else None

    # Init context
    if context is None:
        context = {
            'I': I,
            'Q': INIT_Q(I),
            'Q_EFFORTS': [random.randint(1,2)       for x in range(6)] + [random.randint(0,1)  for x in range(6)],
            'Q_TIMES':   [random.randint(0,300)     for x in range(6)] + [random.randint(0,180) for x in range(6)],
            'Q_VALUES':  ['R1', 'R1', ['Id'], 'R1', [[],[],[],[],[]], [[],[],[],[],[]]] + ANSWERS,
            'Q_SCORES':  [random.randint(0,1)       for x in range(6)] + [1]*6,
            'PREV_TS': 0
        }
    
    # Move to next layout
    elif button and context['I'] in range(15):

        # Store user's answser if current layout is a question
        if context['I'] in range(1,7) or context['I'] in range(8,14):
            
            # Set default value if value omitted
            q_effort   = q_effort    if q_effort    else 1
            q_release  = q_release   if q_release   else 'R3'
            q_posts    = q_posts     if q_posts     else []
            q_badges   = q_badges    if q_badges    else []
            q_users    = q_users     if q_users     else []
            q_votes    = q_votes     if q_votes     else []
            q_comments = q_comments  if q_comments  else []
            
            # Prepare answsers values depending on questions Q
            values = [
                q_release,
                q_release,
                q_posts,
                q_release,
                [q_badges, q_comments, q_posts, q_users, q_votes],
                [q_badges, q_comments, q_posts, q_users, q_votes],
            ]
            
            # Store questions metrics
            context['Q_VALUES'] [context['Q']] = values[context['Q']%6]
            context['Q_EFFORTS'][context['Q']] = q_effort
            context['Q_TIMES']  [context['Q']] = (timestamp-context['PREV_TS'])/1000
            context['Q_SCORES'] [context['Q']] = score( values[context['Q']%6], ANSWERS[context['Q']%6] )
            
            #print(context['Q_VALUES'][context['Q']], context['Q_EFFORTS'][context['Q']], context['Q_TIMES'][context['Q']], context['Q_SCORES'] [context['Q']])
            
            context['Q'] += 1

        
        # On every click, take time and move pointer to next layout 
        context['PREV_TS'] = timestamp
        context['I'] += 1
    
    if button_end:
        context['I'] = 14
    
    return json.dumps(context)



 