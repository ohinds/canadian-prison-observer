"""App to reveal the scale and shape of the Canadian carceral system.
"""

import dash
from dash.dependencies import Input, Output
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

pies = {
    'population': Pie('population'),
    'admissions': Pie('admissions')
}
for pie in pies.values():
    pie.build()
year_slider_marks = {i: {'label': f'{i}/{i+1}'} for i in range(2000, 2018)}

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
                dcc.Dropdown(
                    id='pie-dropdown',
                    options=[{'label': pie_name.title(), 'value': pie_name} for pie_name in pies]
                ),
                dcc.Slider(
                    id='year-slider',
                    min=min(year_slider_marks),
                    max=max(year_slider_marks),
                    value=max(year_slider_marks),
                    marks=year_slider_marks,
                ),
                dcc.Graph(
                    id='pie',
                    figure={},
                    config={'displayModeBar': False}
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
        return {}
    pies[pie_name].build(year=year_slider_marks[year]['label'])
    return pies[pie_name].get_figure()


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
