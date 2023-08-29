from dash import Dash, html, dcc, callback, Output, Input, dash_table
from pathlib import Path

import plotly.express as px
import pandas as pd
import json

##### DATAFRAME #####

data = json.loads(Path('data.json').read_text(encoding='utf-8'))
gods = json.loads(Path('gods.json').read_text(encoding='utf-8'))
weapons = json.loads(Path('weapons.json').read_text(encoding='utf-8'))

rings, cuffs, spells, companions = [], [], [], []
imgs = {}

for build in data:
    
    for equipment in build['equipments']:
        if equipment['type'] == 1:
            rings.append({
                'name':equipment['name_fr'],
                'god':gods[str(build['god_id'])],
                'weapon':weapons[str(build['weapon_id'])],
                'views':build['views'],
                'likes':build['likes_count'],
            })
        elif equipment['type'] == 2:
            cuffs.append({
                'name':equipment['name_fr'],
                'god':gods[str(build['god_id'])],
                'weapon':weapons[str(build['weapon_id'])],
                'views':build['views'],
                'likes':build['likes_count'],
            })
        else:
            raise Exception(f"Equipment type unknow : {equipment['type']}")
        imgs[equipment['name_fr']] = f"![{equipment['name_fr']}](https://wavendb.com/img/equipment/{equipment['img']}.png)"

        
    for spell in build['spells']:
        spells.append({
            'name':spell['name_fr'],
            'god':gods[str(build['god_id'])],
            'weapon':weapons[str(build['weapon_id'])],
            'views':build['views'],
            'likes':build['likes_count'],
        })
        imgs[spell['name_fr']] = f"![{spell['name_fr']}](https://wavendb.com/img/spells/{spell['img']}.png)"

    for companion in build['companions']:
        companions.append({
            'name':companion['name_fr'],
            'god':gods[str(build['god_id'])],
            'weapon':weapons[str(build['weapon_id'])],
            'views':build['views'],
            'likes':build['likes_count'],
        })
        imgs[companion['name_fr']] = f"![{companion['name_fr']}](https://wavendb.com/img/companions/{companion['img']}.png)"

rings = pd.DataFrame(rings)
cuffs = pd.DataFrame(cuffs)
spells = pd.DataFrame(spells)
companions = pd.DataFrame(companions)

def filter_table(df, gods, weapons):
    fdf = df.copy()
    if gods != None:
        fdf = fdf[fdf['god'].isin(gods)]
    if weapons != None:
        fdf = fdf[fdf['weapon'].isin(weapons)]
    return fdf

def arrange_table(df):
    count = df.groupby('name')['views'].count()
    vsum = df.groupby('name')['views'].sum()
    vmean = df.groupby('name')['views'].mean()
    lsum = df.groupby('name')['likes'].sum()
    lmean = df.groupby('name')['likes'].mean()

    rows = []
    for name, c, vs, vm, ls, lm in zip(count.index, count.values, vsum.values, vmean.values, lsum.values, lmean.values):
        rows.append({
            'name':name, 
            'img':imgs[name],
            'occ':c,
            'view_occ':vs, 
            'view_mean':vm,
            'like_occ':ls,
            'like_mean':lm
        })
    return rows

##### APP #####

COLUMNS = [
    {'id':'name', 'name':'name'},
    {'id':'img', 'name':'img', 'presentation':'markdown'},
    {'id':'occ', 'name':'occ'},
    {'id':'view_occ', 'name':'view_occ'},
    {'id':'view_mean', 'name':'view_mean'},
    {'id':'like_occ', 'name':'like_occ'},
    {'id':'like_mean', 'name':'like_mean'},
]

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Waven Trends', style={'textAlign':'center'}),
    dcc.Dropdown(list(gods.values()), list(gods.values()), multi=True, id='dropdown-selection-gods'),
    dcc.Dropdown(list(weapons.values()), list(weapons.values()), multi=True, id='dropdown-selection-weapons'),
    html.Div(id="table-content-rings", style={'display':'flex', 'columnGap':'20px'}),
])

@callback(
    Output('table-content-rings', 'children'),
    Input('dropdown-selection-gods', 'value'),
    Input('dropdown-selection-weapons', 'value'),
)
def update_graph(gods, weapons):
    return [
        html.Div(children=[html.H2(children='Rings'), dash_table.DataTable(
            arrange_table(filter_table(rings, gods, weapons)), 
            columns=COLUMNS,
            sort_action="native", 
            sort_by=[{'column_id':'occ','direction':'desc'}])],
        ),
        html.Div(children=[html.H2(children='Cuffs'), dash_table.DataTable(
            arrange_table(filter_table(cuffs, gods, weapons)),
            columns=COLUMNS,
            sort_action="native", 
            sort_by=[{'column_id':'occ','direction':'desc'}])]
        ),
        html.Div(children=[html.H2(children='Spells'), dash_table.DataTable(
            arrange_table(filter_table(spells, gods, weapons)),
            columns=COLUMNS,
            sort_action="native",
            sort_by=[{'column_id':'occ','direction':'desc'}])]),
        html.Div(children=[html.H2(children='Companions'), dash_table.DataTable(
            arrange_table(filter_table(companions, gods, weapons)),
            columns=COLUMNS,
            sort_action="native",
            sort_by=[{'column_id':'occ','direction':'desc'}])]),
    ]

if __name__ == '__main__':
    app.run(debug=True) 