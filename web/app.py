"""App to reveal the scale and shape of the Canadian carceral system.
"""

import dash
from dash.dependencies import ClientsideFunction, Input, Output
import dash_core_components as dcc
import dash_html_components as html

from visualize.pie import Pie



app = dash.Dash(
    __name__,
    meta_tags=[
        {'name': 'viewport',
         'content': 'width=device-width, initial-scale=1.0'}
    ],
)
app.title = "The Canadian Carceral System"
server = app.server

population_pie = Pie('population', year='2017/2018')
population_pie.build()

app.layout = html.Div(
    id='root',
    children=[
        html.Div(
            html.Div("The Canadian Carceral System",
                     className='title sans'),
            id='title',
        ),
        html.Div(
            id='app-container',
            className='row flex-display',
            children=[
                dcc.Graph(
                    id='pie',
                    figure=population_pie.get_figure(),
                    config={'displayModeBar': False}
                ),
            ]
        ),
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
