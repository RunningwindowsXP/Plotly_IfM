# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import pyodbc

# Incorporate data
conn_str = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    r'DBQ=C:\Users\koep\Downloads\Beispiel-Datenbank.accdb;'
)
conn = pyodbc.connect(conn_str)

df = pd.read_sql("SELECT * FROM Wirtschaftzweige", conn)
conn.close()
# Use a label column so the legend shows real Umsatzklasse names.
# Ersetze die Bezeichnungen hier mit den echten Namen aus deiner Datenbank.
umsatzklasse_label_map = {
    1: '1 - bis 2 Mio. Euro',
    2: '2 - 2 bis 10 Mio. Euro',
    3: '3 - 10 bis 25 Mio. Euro',
    4: '4 - 25 bis 50 Mio. Euro',
    5: '5 - über 50 Mio. Euro'
}
df['Umsatzklassen'] = df['Umsatzklasse'].map(umsatzklasse_label_map).fillna(df['Umsatzklasse'].astype(str))
# Initialize the app - incorporate css
external_stylesheets = ['stylesheet.css']
app = Dash(external_stylesheets=external_stylesheets)

# App layout
app.layout = [
    html.Div(className='row', children='My First App with Data, Graph, and Controls',
             style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30}),

    html.Div(className='row', children=[
        dcc.RadioItems(options=['Wirtschaftszweig', 'Umsatzklasse', 'Beschäftigtenklasse'],
                       value='Wirtschaftszweig',
                       inline=True,
                       id='my-radio-buttons-final')
    ]),

    html.Div(className='row', children=[
        html.Div(className='twelve columns', children=[
            dcc.Graph(
                figure={},
                id='histo-chart-final',
                style={'height': '700px'},
                config={'displayModeBar': False}
            )
        ])
    ]),

    html.Div(className='row', children=[
        html.Div(className='twelve columns', children=[
            dag.AgGrid(
                rowData=df.to_dict('records'),
                columnDefs=[{"field": i} for i in df.columns]
            )
        ])
    ])
]

# Add controls to build the interaction
@callback(
    Output(component_id='histo-chart-final', component_property='figure'),
    Input(component_id='my-radio-buttons-final', component_property='value')
)
def update_graph(col_chosen):
    fig = px.histogram(
        df,
        x=col_chosen,
        y='Umsatz in 1000€',
        color='Umsatzklassen',
        histfunc='sum',
        title=f'Summe von {col_chosen} nach Umsatz in 1000€',
        color_discrete_sequence=["#FFA200", "#DF8200", '#BF6200', '#9F4200', '#7F2200']
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

# Run the app
if __name__ == '__main__':
    app.run(debug=True)