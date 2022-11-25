from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
from dateutil.parser import parse
import plotly.express as px
import warnings

from utils import *

warnings.filterwarnings('ignore')


# load dataset
ld = LoadDframe()
df = ld.load('./dataset/Consumo_cerveja.csv')

# create objects
t = Temperature()
model = Model('./model/model.pkl')

# days
today = parse('31/12/2015', dayfirst=True)
tomorrow = today + timedelta(1)

# get weather information
today_weather = t.get_temperature(today)
tomorrow_weather = t.get_temperature(tomorrow)

# predictions
pred_today = model.predict(float(today_weather['tmax']), float(today_weather['pmax']), parse('31/12/2015'))
pred_tomorrow = model.predict(float(tomorrow_weather['tmax']), float(tomorrow_weather['pmax']), parse('01/01/2015'))

app = Dash(external_stylesheets=[dbc.themes.DARKLY])

navbar = dbc.NavbarSimple(
    brand='DashBoard Consumo de Cerveja',
    brand_href='#',
    color='primary',
    dark=True
)

card_temp = [
    dbc.CardHeader("Temperatura"),
    dbc.CardBody(
        [
            html.P(f"Hoje {'/'.join(today_weather['data'].split('-')[:-1])}", className="card-text"),
            html.H4(f"Max: {today_weather['tmax']}° Min: {today_weather['tmin']}°"),
            html.P(f"Amanhã {'/'.join(tomorrow_weather['data'].split('-')[:-1])}", className="card-text"),
            html.H4(f"Max: {tomorrow_weather['tmax']}° Min: {tomorrow_weather['tmin']}°"),
        ]
    ),
]

card_chuva = [
    dbc.CardHeader("Precipitação"),
    dbc.CardBody(
        [
            html.P(f"Hoje {'/'.join(today_weather['data'].split('-')[:-1])}", className="card-text"),
            html.H4(f"Max: {today_weather['pmax']}mm"),
            html.P(f"Amanhã {'/'.join(tomorrow_weather['data'].split('-')[:-1])}", className="card-text"),
            html.H4(f"Max: {tomorrow_weather['pmax']}mm"),
        ]
    ),
]

card_previsto = [
    dbc.CardHeader("Venda Esperada"),
    dbc.CardBody(
        [
            html.P(f"Hoje {today.strftime('%d/%m')}", className="card-text"),
            html.H4(f"{FormatNum.format_float(round(pred_today[0], 2))} Litros"),
            html.P(f"Amanhã {tomorrow.strftime('%d/%m')}", className="card-text"),
            html.H4(f"{FormatNum.format_float(round(pred_tomorrow[0], 2))} Litros"),
        ]
    ),
]

card_venda_realizada = [
    dbc.CardHeader("Venda Realizada"),
    dbc.CardBody(
        [
            html.P(f"Hoje {today.strftime('%d/%m')}", className="card-text"),
            html.H4(f"{FormatNum.format_int(df.loc[today.strftime('%Y-%m-%d'), 'consumo'])} Litros"),
            html.H4(f"{df.loc[today.strftime('%Y-%m-%d'), 'dif_pct_consumo'] * 100}%"),
            html.P('Em relação a ontem')
        ]
    ),
]

cards = dbc.Row(
    [
        dbc.Col(dbc.Card(card_temp, color='light', outline=True), md=3),
        dbc.Col(dbc.Card(card_chuva, color='light', outline=True), md=3),
        dbc.Col(dbc.Card(card_previsto, color='light', outline=True), md=3),
        dbc.Col(
            dbc.Card(
                card_venda_realizada, outline=True,
                color='success' if df.loc[today.strftime('%Y-%m-%d'), 'dif_pct_consumo'] > 0 else 'danger'
            ), md=3
        )
    ]
)


fig_year_line = html.Div(
    dbc.Card(
        dbc.CardBody(
            dcc.Graph(
                id='figure_year_line',
                figure=px.line(
                    df.reset_index(), x='data', y='consumo', hover_data=['temp_max', 'chuva', 'fds'],
                    color_discrete_sequence=[px.colors.qualitative.Set3[4]], height=400
                ).update_layout(
                    template='plotly_dark', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)',
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='white'),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='white')
                )
            )
        ), color='light', outline=True
    )
)

fig_year_pie = html.Div(
    dbc.Card(
        dbc.CardBody(
            dcc.Graph(
                id='figure_year_pie',
                figure=px.pie(
                    df, values='consumo', names='mes', hole=.45, height=400, width=370,
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    category_orders={
                        'mes': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                    }
                ).update_traces(
                    textposition='inside', textinfo='percent+label', showlegend=False
                ).update_layout(
                    annotations=[
                        dict(text='Total', x=0.5, y=0.6, font_size=20, showarrow=False),
                        dict(
                            text=format(df.consumo.sum(), ',d').replace(',', '.'), x=0.5, y=0.5, font_size=20,
                            showarrow=False
                        )
                    ], template='plotly_dark', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)'
                )
            )
        ), color='light', outline=True
    )
)

fig_year_bar = html.Div(
    dbc.Card(
        dbc.CardBody(
            dcc.Graph(
                id='figure_year_bar',
                figure=px.histogram(
                    df, x='mes', y='consumo', color='fds', barmode='relative', histfunc='sum',
                    color_discrete_sequence=px.colors.qualitative.Set3[3:5], height=400
                ).update_layout(
                    template='plotly_dark', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)',
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='white'),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='white')
                )
            )
        ), color='light', outline=True
    )
)

fig_days_pie = html.Div(
    dbc.Card(
        dbc.CardBody(
            dcc.Graph(id='figure_days_pie')
        ), color='light', outline=True
    )
)

fig_relational_temp = html.Div(
    dbc.Card(
        dbc.CardBody(
            dcc.Graph(
                id='figure_retational_temp',
                figure=px.scatter(
                    df, x='temp_max', y='consumo', color='fds', color_discrete_sequence=px.colors.qualitative.Set3[3:5],
                    height=400
                ).update_layout(
                    template='plotly_dark', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)',
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='white'),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='white')
                )
            )
        ), color='light', outline=True
    )
)

fig_relational_chuva = html.Div(
    dbc.Card(
        dbc.CardBody(
            dcc.Graph(
                id='figure_retational_chuva',
                figure=px.scatter(
                    df, x='chuva', y='consumo', color='fds', color_discrete_sequence=px.colors.qualitative.Set3[3:5],
                    height=400
                ).update_layout(
                    template='plotly_dark', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)',
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='white'),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='white')
                )
            )
        ), color='light', outline=True
    )
)

figs1 = dbc.Row(
    [
        dbc.Col(fig_year_line, md=8),
        dbc.Col(fig_year_pie, md=4)
    ]
)

figs2 = dbc.Row(
    [
        dbc.Col(fig_year_bar, md=8),
        dbc.Col(fig_days_pie, md=4)
    ]
)

figs3 = dbc.Row(
    [
        dbc.Col(fig_relational_temp, md=6),
        dbc.Col(fig_relational_chuva, md=6)
    ]
)

select = dbc.Select(
    id="select",
    options=[
        {'label': 'Janeiro', 'value': 'Jan'},
        {'label': 'Feveiro', 'value': 'Fev'},
        {'label': 'Março', 'value': 'Mar'},
        {'label': 'Abril', 'value': 'Abr'},
        {'label': 'Maio', 'value': 'Mai'},
        {'label': 'Junho', 'value': 'Jun'},
        {'label': 'Julho', 'value': 'Jul'},
        {'label': 'Agosto', 'value': 'Ago'},
        {'label': 'Setembro', 'value': 'Set'},
        {'label': 'Outubro', 'value': 'Out'},
        {'label': 'Novembro', 'value': 'Nov'},
        {'label': 'Dezembro', 'value': 'Dez'}
    ], value='Jan'
)

app.layout = dbc.Container(
    [
        navbar, html.Br(), cards, html.Br(), figs1, html.Br(), dbc.Row(dbc.Col(select, md=2), justify='end'), figs2,
        html.Br(), figs3, html.Br()
    ], fluid=True
)


@app.callback(
    Output('figure_days_pie', 'figure'),
    Input('select', 'value')
)
def gen_graph(value):
    fig = px.pie(
        df.query(f"mes == '{value}'"), values='consumo', names='dia', hole=.45, height=400, width=350,
        color_discrete_sequence=px.colors.qualitative.Set3,
        category_orders={'dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']}
    ).update_traces(
        textposition='inside', textinfo='percent+label', showlegend=False
    ).update_layout(
        annotations=[
            dict(text=FormatNum.format_int(df.query(f"mes == '{value}'").consumo.sum()), x=0.5, y=0.5, font_size=20,
                 showarrow=False),
            dict(text='Total', x=0.5, y=0.6, font_size=20, showarrow=False)
        ], template='plotly_dark', plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)'
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
