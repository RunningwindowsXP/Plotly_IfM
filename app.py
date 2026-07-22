from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import sqlite3

conn = sqlite3.connect("daten_neu.db")

df = pd.read_sql("SELECT * FROM Wirtschaftszweige", conn)
conn.close()


umsatzklasse_label_map = {
    1: '1 - bis 2 Mio. Euro',
    2: '2 - 2 bis 10 Mio. Euro',
    3: '3 - 10 bis 25 Mio. Euro',
    4: '4 - 25 bis 50 Mio. Euro',
    5: '5 - über 50 Mio. Euro'
}

df['Umsatzklasse'] = df['Umsatzklasse'].map(umsatzklasse_label_map).fillna(df['Umsatzklasse'].astype(str))


app = Dash()

app.layout = [

    html.Div(
        className='row',
        children='Beispiel Dashboard des IfM Bonn',
        style={
            'textAlign': 'center',
            'color': 'blue',
            'fontSize': 30
        }
    ),

    html.Div(
        className='row',
        children='von: Jonathan Maier, Johannes Koep',
        style={
            'textAlign': 'center',
            'color': 'black',
            'fontSize': 12
        }
    ),

    html.Div(className='spacer'),


    # Parameter + Histogramm
    html.Div(className='row', children=[

        html.Div(className='three columns', children=[
            html.H5("Y-Achse"),
            dcc.RadioItems(
                options=[
                    'Wirtschaftszweig',
                    'Umsatzklasse',
                    'Beschäftigtenklasse'
                ],
                value='Wirtschaftszweig',
                id='y_axis'
            ),
            html.Div(className='spacer'),
            html.H5("Jahr"),
            dcc.Slider(
                min=2022,
                max=2024,
                step=1,
                value=2024,
                id='year_slider'
            ),
            html.Div(className='spacer'),
            dcc.RadioItems(
                options=[
                    'Jahre kumulieren',
                    'Einzelnes Jahr',
                ],
                value='Jahre kumulieren',
                id='kumulieren_auswahl'
            ),
            html.Div(className='spacer'),
            html.H5("Färbung"),
            dcc.RadioItems(
                options=[
                    'Umsatzklasse',
                    'Jahr',
                ],
                value='Umsatzklasse',
                id='faerbung'
            )
        ]),

        html.Div(className='nine columns', children=[
            dcc.Graph(
                figure={},
                id='Wirtschaftszweige_Histogramm',
                style={'height': '450px'},
                config={'displayModeBar': False}
            )
        ])
    ]),

    html.Div(className='spacer'),

    # Tabelle separat unten
    html.Div(className='row', children=[

        html.Div(className='twelve columns', children=[
            dag.AgGrid(
                rowData=df.to_dict('records'),
                columnDefs=[
                    {"field": i}
                    for i in df.columns
                ]
            )
        ])
    ])
]


@callback(
    Output(component_id='Wirtschaftszweige_Histogramm', component_property='figure'),
    Input(component_id='y_axis', component_property='value'),
    Input(component_id='year_slider', component_property='value'),
    Input(component_id='kumulieren_auswahl', component_property='value'), 
    Input(component_id='faerbung', component_property='value')
)
def update_graph(col_chosen, year, kumulieren, faerbung):
    conn = sqlite3.connect("daten_neu.db")

    if kumulieren == "Einzelnes Jahr":
        df = pd.read_sql("SELECT * FROM Wirtschaftszweige WHERE Jahr = ?", conn, params=(year,))
    elif kumulieren == "Jahre kumulieren":
        df = pd.read_sql("SELECT * FROM Wirtschaftszweige WHERE Jahr <= ?", conn, params=(year,))
    conn.close()

    df['Umsatzklasse'] = df['Umsatzklasse'].map(umsatzklasse_label_map).fillna(df['Umsatzklasse'].astype(str))   
    
    if faerbung == "Umsatzklasse":
        palette = ["#FFA200", "#DF8200", '#BF6200', '#9F4200', '#7F2200']
    elif faerbung == "Jahr":
        palette = ["#00FF1A", "#5AFFAE", "#66F0FF"]

    fig = px.histogram(
        df,
        x=col_chosen,
        y='Umsatz in 1000€',
        color=faerbung,
        histfunc='sum',
        title=f'Summe von {col_chosen} nach Umsatz in 1000€',
        color_discrete_sequence=palette
    )
    fig.update_layout(
        yaxis_title=f'Summe des Umsatzes in 1000€ nach {col_chosen}',
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(l=50, r=140, t=70, b=50),
        bargap=0.18,
        xaxis=dict(
            tickangle=0,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            gridcolor='rgba(0,0,0,0.08)',
            zeroline=False
        ),
        title=dict(x=0.5, xanchor='center', font=dict(size=20)),
        legend=dict(
            orientation='v',
            x=1.02,
            y=1,
            bordercolor='rgba(0,0,0,0)',
            bgcolor='rgba(255,255,255,0.9)',
            itemclick='toggleothers'
        )
    )
    return fig

if __name__ == '__main__':
    app.run(host="0.0.0.0",
            port=20002,
            debug=True)