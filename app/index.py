
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app  import app
from apps import game, views, raw



app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])



@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if   pathname == '/game':
         return game.layout
    elif pathname == '/raw':
         return raw.layout         
    elif pathname == '/views':
         return views.layout
    else:
        return game.layout



if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
    
    
 