from plotly.graph_objs import *
import numpy as np
import networkx as nx


def draw_network_graph(df, weights):
    """function draws a network graph of the supplied dataframe,
    the size of nodes equaling to the supplied weights
    returns data and layout needed to create the figure
    """
    g = nx.from_pandas_dataframe(df, 'author', 'coauthor', edge_attr='weight')
    pos = nx.fruchterman_reingold_layout(g)
    names = np.unique(df[['author', 'coauthor']].values)
    # get layout positions - vertices
    Xv = [pos.get(k)[0] for k in names]
    Yv = [pos.get(k)[1] for k in names]
    # get labels
    labels = [k for k in names]
    # get sizes
    size = [weights.get(label) for label in labels]
    sizes = [(lambda i: 27 if i > 25 else i)(i) for i in size]
    # create edges
    Xed, Yed, Xmed, Ymed, widths = [], [], [], [], []
    edges, hinfo = [], []
    for i in range(len(names)):
        if size[i] > 1:
            hinfo.append(str(labels[i]) + " has " + str(size[i]) + " publications")
        else:
            hinfo.append(str(labels[i]) + " has " + str(size[i]) + " publication")
    for i in range(0, len(df)):
        edges.append([df.author[i], df.coauthor[i]])
        if int(df.weight[i]) > 1:
            widths.append(str(df.author[i]) + " and " + str(df.coauthor[i]) + " have " + str(df.weight[i]) + " publications")
        else:
            widths.append(str(df.author[i]) + " and " + str(df.coauthor[i]) + " have " + str(df.weight[i]) + " publication")
    for edge in edges:
        Xed += [pos.get(edge[0])[0], pos.get(edge[1])[0], None]
        Xmed += [(pos.get(edge[0])[0] + pos.get(edge[1])[0]) / 2]
        Yed += [pos.get(edge[0])[1], pos.get(edge[1])[1], None]
        Ymed += [(pos.get(edge[0])[1] + pos.get(edge[1])[1]) / 2]

    #create graph layout
    layout = Layout(title="Coauthorship network of scientists working on selected unit",
                    font=dict(size=12),
                    showlegend=False,
                    height=600,
                    xaxis=dict(showline=False, zeroline=False, showgrid=False, showticklabels=False, title=''),
                    yaxis=dict(showline=False, zeroline=False, showgrid=False, showticklabels=False, title=''),
                    margin=dict(l=40, r=40, b=30, t=100,),
                    hovermode='closest',
                    )

    #create edges
    trace1 = Scatter(x=Xed,
                     y=Yed,
                     mode='lines',
                     line=dict(color='rgb(210,210,210)', width=1),
                     hoverinfo='none'
                     )
    #create vertices
    trace2 = Scatter(x=Xv,
                     y=Yv,
                     mode='markers',
                     name='net',
                     marker=dict(symbol='circle-dot',
                                 size=sizes,
                                 color='#6959CD',
                                 line=dict(color='rgb(50,50,50)', width=0.5)
                                 ),
                     text=hinfo,
                     hoverinfo='text'
                     )
    #create invisible middle nodes for weigh of connection on hover
    middle_node_trace = Scatter(
                    x=Xmed,
                    y=Ymed,
                    text=widths,
                    mode='markers',
                    hoverinfo='text',
                    marker=Marker(
                        opacity=0
                        )
                    )

    data = [trace1, trace2, middle_node_trace]

    return data, layout


def draw_histogram(x, y, name):
    """function for drawing a histogram plot of
    two suppled arguments, with title supplied as name
    returns ready figure"""
    widths = [0.5 for i in range(len(x))]
    if len(x) == 1:
        widths = [0.1]
    figure={
            'data': [{
                'x': x,
                'y': y,
                'width': widths,
                'type': 'bar'
            }],
            'layout': {
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)',
                'autosize': True,
                'margin': '0px 0px 0px 0px',
                'title': name
            }
        }
    return figure
