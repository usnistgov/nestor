"""__author__ = "Thurston Sexton" """

import networkx as nx

from sklearn.preprocessing import MultiLabelBinarizer#, minmax_scale
from sklearn.metrics.pairwise import cosine_similarity

import pandas as pd
import numpy as np
from tqdm import tqdm



def node_adj_mat(tag_df, similarity='cosine', dag=False, pct_thres=None):
    """
    Calculate the similarity of tags, in the form of a similarity kernel.
    Used as input to graph/network methods.

    Parameters
    ----------
    tag_df: pandas.DataFrame
        standard Nestor tag occurrence matrix. Multi-column with top-level containing
        tag classifications (named-entity NE) and 2nd level containing tags. Each row
        corresponds to a single event (MWO), with binary indicators (1-occurs, 0-does not).
    similarity: str
        cosine: cosine similarity (from ``sklearn.metrix.pairwise``)
        count: count (the number of co-occurrences of each tag-tag pair)
    dag: bool
        default adj_mat will be accross all nodes. This option will return a
        directed, acyclic graph (DAG), useful for things like Sankey Diagrams.
        Current implementation returns (P) -> (I) -> (S) structure (deletes others).
    pct_thres: int or None
        If int, between [0,100]. The lower percentile at which to threshold edges/adjacency.

    Returns
    -------
    pandas.DataFrame, containing adjacency measures for each tag-tag (row-column) occurrence
    """
    adj_mat = tag_df.T.dot(tag_df)

    if similarity is 'cosine':
        adj_mat.loc[:, :] = cosine_similarity(tag_df.T)
    else:
        assert similarity is 'count', "Similarity must be one of ['cosine', 'count']!"
    np.fill_diagonal(adj_mat.values, 0)

    if dag:
        for NE in 'IPS':
            adj_mat.loc[NE,NE] = 0.  # no self-self
        adj_mat.loc['P', 'S'] = 0.   # no action-action
        adj_mat.loc['S', 'P'] = 0.
        adj_mat.loc['I', 'P'] = 0.   # ensure DAG
        adj_mat.loc['S', 'I'] = 0.   # (P)->(I)->(S)

    if pct_thres is not None:
        assert 0 <= pct_thres <= 100, 'percentiles must be between [0,100]'
        lower = np.percentile(adj_mat, pct_thres)
        adj_mat[adj_mat < lower] = 0.

    return adj_mat


def tag_network(adj_mat, column_lvl=0):
    """
    Takes in an adjacency matrix (pandas.DataFrame, assumes multi-col/row)
    and returns a networkx Graph object with those nodes/edge weights.
    """
    G = nx.from_numpy_matrix(adj_mat.values)
    G = nx.relabel_nodes(G, dict(zip(G.nodes(), adj_mat.columns.get_level_values(column_lvl))))
    return G


def tag_df_network(tag_df, **node_adj_kws):
    """
    Starting from a multi-column binary tag-occurrence pandas.Dataframe (such as
    output by the Nestor UI and the `nestor.keyword.tag_extractor()` method, create
    a networkx graph, along with a node_info and edge_info dataframe for plotting
    convenience (e.g. in nestor.tagplots)

    Parameters
    ----------
    tag_df :  pandas.DataFrame
        standard Nestor tag occurrence matrix. Multi-column with top-level containing
        tag classifications (named-entity NE) and 2nd level containing tags. Each row
        corresponds to a single event (MWO), with binary indicators (1-occurs, 0-does not).
    node_adj_kws :

    Returns
    -------

    """

    adj_mat = node_adj_mat(tag_df, **node_adj_kws)
    G = tag_network(adj_mat, column_lvl=1)

    ct = tag_df.sum().xs(slice(None))  # counts
    nx.set_node_attributes(G, name='count', values=ct.to_dict())

    # size scaling...wait for holoviews `op()` functionality
    # ct_std = np.log(1+(ct-ct.min(axis=0))/(ct.max(axis=0)-ct.min(axis=0)))
    # nx.set_node_attributes(G, 'size', (ct_std*(30-10) + 10).to_dict())

    # add tag classification
    nx.set_node_attributes(G, name='NE',
                           values=dict(tag_df.swaplevel(axis=1).columns.tolist()))

    # Deprecated
    # node_info = pd.concat([pd.DataFrame(nx.layout.spring_layout(G)).T,
    #                        pd.DataFrame.from_dict({k: v for k, v in G.nodes(data=True)}, orient='index')],
    #                       axis=1).reset_index()
    node_info = pd.DataFrame.from_dict({k: v for k, v in G.nodes(data=True)}, orient='index')

    edge_info = adj_mat.copy()
    edge_info.index, edge_info.columns = edge_info.index.droplevel(0), edge_info.columns.droplevel(0)

    # trick to get out source-target relationships with pandas
    edge_info = edge_info.stack(level=0).reset_index()
    edge_info.columns = ['source', 'target', 'weight']
    edge_info = edge_info.replace(0., np.nan)

    # edge_info.weight = np.log(1+edge_info.weight)  # wait for Holoviews `op()` functionality
    
    return G, node_info, edge_info.dropna()


def heymann_taxonomy(dist_mat, cent_prog='pr', tau=5e-4,
                     dynamic=False, dotfile=None, verbose=False):
    """

    Parameters
    ----------
    dist_mat: pandas.DataFrame
        contains similarity matrix, indexed and named by tags
    cent_prog: str
        algorithm to use in calculating node centrality

        pr: PageRank
        eig: eigencentrality
        btw: betweenness
        cls: closeness

    tau: float
        similarity threshold for retaining a node
    dynamic: bool
        whether to re-calculate centrality after popping every tag
    write_dot: str or None
        file location, where to save a .dot, if any.
    verbose: bool
        print some stuff


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

    D.remove_nodes_from(list(nx.isolates(D)))  # not useful for taxonomy

    if dotfile is not None:
        from networkx.drawing.nx_pydot import graphviz_layout, write_dot
        D.graph['graph'] = {'rankdir': 'LR',
                            'splines': 'true',
                            'ranksep': '4'}
        write_dot(D, dotfile)

    return D


######### DEPRECATED ################

def get_relevant(df, col, topn=20):
    """
    DEPRECATED!

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
    """DEPRECATED!"""
    itm_relevant = get_relevant(df, col, topn=topn)
    itm_event = pd.DataFrame(columns=[i[0] for i in itm_relevant if i[0] != u''],
                             data=np.array([i[2] for i in itm_relevant if i[0] != u'']).T)
    return itm_event



