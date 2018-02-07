"""__author__ = "Thurston Sexton, nx2gt adapted from Benjamin Bengfort" """

import networkx as nx

from sklearn.preprocessing import MultiLabelBinarizer#, minmax_scale
import pandas as pd
import numpy as np
from tqdm import tqdm

def get_relevant(df, col, topn=20):
    """

    Parameters
    ----------
    df: a dataframe containing columns of tag assignments (comma-sep, str)
    col: which column to extract
    topn: how many of the top most frequent tags to return

    Returns
    -------
    list of (tag,count,numpy.array) tuples
    """
    tags = [x[1][col].split(', ') for x in df.iterrows()]
    binner = MultiLabelBinarizer().fit(tags)
    vecs = binner.transform(tags)
    counts = vecs.sum(axis=0)
    relevant = [(binner.classes_[i], counts[i], vecs[:, i]) for i in counts.argsort()[-topn:][::-1]]
    return relevant


def get_onehot(df, col, topn=700):
    itm_relevant = get_relevant(df, col, topn=topn)
    itm_event = pd.DataFrame(columns=[i[0] for i in itm_relevant if i[0] != u''],
                             data=np.array([i[2] for i in itm_relevant if i[0] != u'']).T)
    return itm_event


def node_adj_mat(itm_event):
    coocc = itm_event.T.dot(itm_event)
    occ = np.diagonal(np.copy(coocc))

    np.fill_diagonal(coocc.values, 0)
    adj_mat = coocc / np.dot(np.sqrt(occ).T, np.sqrt(occ))
    return adj_mat


def tag_network(adj_mat, column_lvl=0):
    G = nx.from_numpy_matrix(adj_mat.values)
    G = nx.relabel_nodes(G, dict(zip(G.nodes(), adj_mat.columns.get_level_values(column_lvl))))

    return G


def tag_df_network(tag_df):

    adj_mat = 200*node_adj_mat(tag_df)
    G = tag_network(adj_mat, column_lvl=1)
    # print(tag_df.sum().xs(slice(None)))
    ct = tag_df.sum().xs(slice(None))
    ct_std = np.log(1+(ct-ct.min(axis=0))/(ct.max(axis=0)-ct.min(axis=0)))
    nx.set_node_attributes(G, 'count', ct.to_dict())
    nx.set_node_attributes(G, 'size', (ct_std*(30-10) + 10).to_dict())
    nx.set_node_attributes(G, 'NE', dict(tag_df.swaplevel(axis=1).columns.tolist()))

    # node_info = pd.concat([pd.DataFrame(nx.layout.spring_layout(G)).T,
    #                        pd.DataFrame.from_dict({k: v for k, v in G.nodes(data=True)}, orient='index')],
    #                       axis=1).reset_index()
    node_info = pd.DataFrame.from_dict({k: v for k, v in G.nodes(data=True)}, orient='index')
    edge_info = adj_mat.copy()
    edge_info.index, edge_info.columns = edge_info.index.droplevel(0), edge_info.columns.droplevel(0)
    edge_info = edge_info.stack(level=0).reset_index()
    edge_info.columns = ['source', 'target', 'weight']
    edge_info = edge_info.replace(0., np.nan)
    edge_info.weight = np.log(1+edge_info.weight)
    return G, node_info, edge_info.dropna()


def heymann_taxonomy(dist_mat, cent_prog='pr', tau=5e-4,
                     dynamic=False, dotfile=None, verbose=False):
    """
    dist_mat: dataframe containing similarity matrix, indexed and named by tags
    cent_prog: algorithm to use in calculating node centrality
        pr: PageRank
        eig: eigencentrality
        btw: betweenness
        cls: closeness
    tau: similarity threshold for retaining a node
    dynamic: re-calculate centrality after adding every tag
    write_dot: fname or None, where to save a .dot, if any.
    verbose: print some stuff
    """
    #     tau = 5e-4
    cent_dict = {
        'pr': nx.pagerank,
        'eig': nx.eigenvector_centrality,
        'btw': nx.betweenness_centrality,
        'cls': nx.closeness_centrality
    }

    # Create the co-occurence graph, G
    G = nx.from_numpy_matrix(dist_mat.values)
    G = nx.relabel_nodes(G, dict(zip(G.nodes(), dist_mat.columns)))

    # Calculate the centrality of nodes in G
    cent = pd.Series(cent_dict[cent_prog](G)).sort_values(ascending=False)
    root = cent.index[0]
    print(root)

    # Init the taxonomy D (DAG)
    D = nx.DiGraph()
    D.add_node(root)

    for n in tqdm(range(dist_mat.shape[0])):

        # Pick the most central node in G, and the node in D most similar to it
        tag = cent.index[0]
        neighbor_sim = {k: dist_mat.loc[tag, k] for k in D.nodes()}
        parent = max(neighbor_sim, key=lambda key: neighbor_sim[key])

        if neighbor_sim[parent] > tau:
            # above threshold--> direct child
            D.add_node(tag)
            D.add_edge(parent, tag)
        else:
            #         D.add_edge(root, descendant)  # do not enforce single taxonomy
            # New "top-level" tag
            D.add_node(tag)
            pass

        if dynamic:
            # recalculate node centralities after removing each <tag>
            # EXPENSIVE.
            G.remove_node(tag)
            cent = pd.Series(cent_dict[cent_prog](G)).sort_values(ascending=False)
        else:
            cent.drop(tag, inplace=True)

    if verbose:
        print(root)  # most "general" topic
        print(nx.isolates(D))  # child-less nodes (i.e. central AND dissimilar)

    D.remove_nodes_from(nx.isolates(D))  # not useful for taxonomy

    if dotfile is not None:
        from networkx.drawing.nx_pydot import graphviz_layout, write_dot
        D.graph['graph'] = {'rankdir': 'LR',
                            'splines': 'true',
                            'ranksep': '4'}
        write_dot(D, dotfile)

    return D


def nx2gt(nxG):
    """
    Converts a networkx graph to a graph-tool graph.
    """
    # Phase 0: Create a directed or undirected graph-tool Graph
    import graph_tool as gt
    gtG = gt.Graph(directed=nxG.is_directed())

    def get_prop_type(value, key=None):
        """
        Performs typing and value conversion for the graph_tool PropertyMap class.
        If a key is provided, it also ensures the key is in a format that can be
        used with the PropertyMap. Returns a tuple, (type name, value, key)
        """

        # Deal with the value
        if isinstance(value, bool):
            tname = 'bool'

        elif isinstance(value, int):
            tname = 'float'
            value = float(value)

        elif isinstance(value, float):
            tname = 'float'

        elif isinstance(value, str):
            tname = 'string'
            # value = value.encode('ascii', errors='replace')

        elif isinstance(value, dict):
            tname = 'object'

        else:
            tname = 'string'
            value = str(value)

        return tname, value, key

    # Add the Graph properties as "internal properties"
    for key, value in nxG.graph.items():
        # Convert the value and key into a type for graph-tool
        tname, value, key = get_prop_type(value, key)

        prop = gtG.new_graph_property(tname)  # Create the PropertyMap
        gtG.graph_properties[key] = prop      # Set the PropertyMap
        gtG.graph_properties[key] = value     # Set the actual value

    # Phase 1: Add the vertex and edge property maps
    # Go through all nodes and edges and add seen properties
    # Add the node properties first
    nprops = set() # cache keys to only add properties once
    for node, data in nxG.nodes_iter(data=True):

        # Go through all the properties if not seen and add them.
        for key, val in data.items():
            if key in nprops: continue # Skip properties already added

            # Convert the value and key into a type for graph-tool
            tname, _, key  = get_prop_type(val, key)

            prop = gtG.new_vertex_property(tname) # Create the PropertyMap
            gtG.vertex_properties[key] = prop     # Set the PropertyMap

            # Add the key to the already seen properties
            nprops.add(key)

    # Also add the node id: in NetworkX a node can be any hashable type, but
    # in graph-tool node are defined as indices. So we capture any strings
    # in a special PropertyMap called 'id' -- modify as needed!
    gtG.vertex_properties['id'] = gtG.new_vertex_property('string')

    # Add the edge properties second
    eprops = set() # cache keys to only add properties once
    for src, dst, data in nxG.edges_iter(data=True):

        # Go through all the edge properties if not seen and add them.
        for key, val in data.items():
            if key in eprops: continue # Skip properties already added

            # Convert the value and key into a type for graph-tool
            tname, _, key = get_prop_type(val, key)

            prop = gtG.new_edge_property(tname) # Create the PropertyMap
            gtG.edge_properties[key] = prop     # Set the PropertyMap

            # Add the key to the already seen properties
            eprops.add(key)

    # Phase 2: Actually add all the nodes and vertices with their properties
    # Add the nodes
    vertices = {} # vertex mapping for tracking edges later
    for node, data in nxG.nodes_iter(data=True):

        # Create the vertex and annotate for our edges later
        v = gtG.add_vertex()
        vertices[node] = v

        # Set the vertex properties, not forgetting the id property
        data['id'] = str(node)
        for key, value in data.items():
            gtG.vp[key][v] = value # vp is short for vertex_properties

    # Add the edges
    for src, dst, data in nxG.edges_iter(data=True):

        # Look up the vertex structs from our vertices mapping and add edge.
        e = gtG.add_edge(vertices[src], vertices[dst])

        # Add the edge properties
        for key, value in data.items():
            gtG.ep[key][e] = value # ep is short for edge_properties

    # Done, finally!
    return gtG

