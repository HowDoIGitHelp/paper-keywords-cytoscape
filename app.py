import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import plotly.express as px
import json
import random
import pandas as pd
import math

cyto.load_extra_layouts()

app = dash.Dash(__name__)
server = app.server

def makeNode(id,label,size,keywords,opacity):
    return {'data':{'id':id, 'label':label,'size':size, 'keywords':keywords, 'opacity':opacity},'grabbable':False}

def makeEdge(source,target,label,opacity,freq,selectable=True):
    return {'data':{'source':source, 'target':target, 'label':label,'opacity':opacity, 'freq':freq},'selectable':selectable}

graph = []

keypaper_df = pd.read_feather('keypaper.ftr')
paper_metrics_df = pd.read_feather('paper_metrics.ftr')
keywords_df = pd.read_feather('keywords.ftr')
keywords_df = keywords_df.set_index('keyword')
print(keywords_df)

paper_metrics_df = paper_metrics_df.set_index('pk')

for paper in list(paper_metrics_df.index.values):
    try:
        size = math.ceil(paper_metrics_df.loc[paper,'pagerank_5']*10)
    except:
        size = 1
    #print(makeNode(paper,paper_metrics_df.loc[paper,'title'],size,str(keypaper_df[keypaper_df['pk']==paper]['keyword'].to_list()),0.8))
    graph.append(makeNode(paper,paper_metrics_df.loc[paper,'title'],size,str(keypaper_df[keypaper_df['pk']==paper]['keyword'].to_list()),0.8))


addedEdges = []
for keyword in list(keywords_df.index.values):
    keyword_papers = keypaper_df[keypaper_df['keyword']==keyword]['pk'].to_list()
    for pk in keyword_papers:
        for pk2 in keyword_papers:
            if pk != pk2 and (pk,pk2,keyword) not in addedEdges:
                graph.append(makeEdge(pk,pk2,keyword,0.08,keywords_df.loc[keyword,'freq']))
                addedEdges.append((pk,pk2,keyword))
                addedEdges.append((pk2,pk,keyword))


default_cyto_style = [
    {'selector':'edge','style':{'opacity':'data(opacity)','width':1.2,'curve-style': 'bezier'}},
    {'selector':'node','style':{
        'width':'mapData(size, 0, 500, 5,40)',
        'height':'mapData(size, 0, 500, 5, 40)',
        'opacity':'data(opacity)',
        'font-size': '12px',
        'text-valign': 'center',
        'text-halign': 'center',
    }},
]
app.layout = html.Div(
    html.Div(
        className = 'main-area',
        children = [
            cyto.Cytoscape(
                id='cytoscape',
                elements=graph,
                layout={'name': 'cose', 'animate':'false'},
                style={'width': '1500px', 'height': '900px'},
                minZoom = 2,
                maxZoom = 4,
                stylesheet = default_cyto_style
            ),
            html.Div(className='graph-controls', children=[
                html.H1('Paper - Keyword Graph'),
                html.Div(className = 'input-group', children = [
                    dcc.Input(id='filter_nodes',value='', placeholder = 'Highlight Keyword...', type='text')
                ]),
                html.Div(className = 'title-list', children = [
                    html.H2('Click on a node for details',id='title_output')
                ]),
                html.Div(className = 'keyword-list', children = [
                    html.H3('Click on an edge for details',id='keyword_output')
                ]),
                html.Div(className = 'input-group', children = [
                    #dcc.Input(id='keyword_freq_threshold', value = '10', type='text')
                ]),
            ])
        ]
    )
)
@app.callback(Output('cytoscape','stylesheet'),
    Input('filter_nodes','value'),
    #Input('keyword_freq_threshold','value')
)
def filter_nodes(filter):
    filter = filter.lower()
    if filter is not None and filter != '':
        filtered_papers = keypaper_df[keypaper_df['keyword']==filter]['pk'].to_list()
        edge_selector = ''
        for paper in filtered_papers:
            edge_selector += 'edge[source=\"'+str(paper)+'\"],edge[target=\"'+str(paper)+'\"],'
        return [
            {'selector':'edge','style':{'opacity':0.00,'width':1.2,'curve-style': 'bezier'}},
            {'selector':'node','style':{
                'width':'mapData(size, 0, 500, 5,40)',
                'height':'mapData(size, 0, 500, 5, 40)',
                'opacity':0.1,
                'font-size': '12px',
                'text-valign': 'center',
                'text-halign': 'center',
            }},
            {'selector':edge_selector[:-1],'style':{'opacity':0.1,'width':2,'curve-style': 'bezier'}},
            {'selector':'edge[label=\"'+filter+'\"]','style':{'opacity':0.05,'width':1.2,'curve-style': 'bezier'}},
            {'selector':'node[keywords*=\"'+filter+'\"]','style':{
                'width':'mapData(size, 0, 500, 5,40)',
                'height':'mapData(size, 0, 500, 5, 40)',
                'opacity':'data(opacity)',
                'font-size': '12px',
                'text-valign': 'center',
                'text-halign': 'center',
            }},
        ]
    else:
        return default_cyto_style


@app.callback(Output('title_output','children'),
    Input('cytoscape','selectedNodeData'))
def show_node_title(selectedNodes):
    if selectedNodes is not None and len(selectedNodes) != 0:
        selectedPapers = ''
        for node in selectedNodes:
            selectedPapers += node['label'] + ', '
        return selectedPapers
    else:
        return 'select node/s for more details'


@app.callback(Output('keyword_output','children'),
    Input('cytoscape','selectedEdgeData'))
def show_edge_keyword(selectedEdges):
    if selectedEdges is not None and len(selectedEdges) != 0:
        selectedKeywords = set()
        for edge in selectedEdges:
            selectedKeywords.add(edge['label'])

        outString = ''
        for keyword in selectedKeywords:
            outString += keyword + ', '
        return outString
    else:
        return 'select edge/s for more details'

if __name__ == '__main__':
    app.run_server(debug=True)
