"""App to reveal the scale and shape of the Canadian carceral system.
"""

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

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

pies = {
    'population': Pie('population'),
    'admissions': Pie('admissions')
}
for pie in pies.values():
    pie.build()
year_slider_marks = {i: {'label': f'{i}/{i+1}'} for i in range(2000, 2018)}

empty_layout = {
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'xaxis': dict(
        showline=False, showgrid=False, zeroline=False, showticklabels=False
    ),
    'yaxis': dict(
        showgrid=False, showline=False, zeroline=False, showticklabels=False
    ),
}


app.layout = html.Div(
    id='root',
    children=[
        html.Div(
            html.Div("The Canadian Carceral System",
                     className='h1'),
            id='title',
        ),
        html.Div(
            id='app-container',
            children=[
                dcc.Dropdown(
                    id='pie-dropdown',
                    options=[{'label': pie_name.title(), 'value': pie_name}
                             for pie_name in pies]
                ),
                html.Div(
                    id='pie-container',
                    className='row flex-display',
                    children=[
                        html.Div(
                            dcc.Slider(
                                id='year-slider',
                                min=min(year_slider_marks),
                                max=max(year_slider_marks),
                                value=max(year_slider_marks),
                                marks=year_slider_marks,
                                vertical=True,
                            ),
                            className='one column',
                        ),
                        html.Div(
                            dcc.Graph(
                                id='pie',
                                figure=go.Figure(layout=empty_layout),
                                config={'displayModeBar': False},
                            ),
                            className='eleven columns',
                        )
                    ]
                ),
            ]
        ),
    ]
)


@app.callback(Output('pie', 'figure'), [
    Input('pie-dropdown', 'value'),
    Input('year-slider', 'value'),
])
def choose_pie(pie_name, year):
    if not pie_name:
        return go.Figure(layout=empty_layout)
    pies[pie_name].build(year=year_slider_marks[year]['label'])
    return pies[pie_name].get_figure()


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
