import argparse

import altair as alt
import numpy as np
import pandas as pd

from sklearn.manifold import TSNE

import streamlit as st

from neo4j_utils import Neo4jConnection


parser = argparse.ArgumentParser(description='Add uri, user, and pwd for Neo4j connection.')
parser.add_argument('uri', type=str, default=None)
parser.add_argument('user', type=str, default='neo4j')
parser.add_argument('pwd', type=str, default=None)

args=parser.parse_args()

neo4j_utils = Neo4jConnection(uri=args.uri, user=args.user, pwd=args.pwd)

st.set_page_config(layout="wide")

##############################
#
#   Sidebar content
#
############################## 

def get_node_labels():

    label_ls = []
    label_type_query = """CALL db.labels()"""
    result = neo4j_utils.query(label_type_query)
    for el in result:
        #st.write(el[0])
        label_ls.append(el[0])
    return label_ls


def get_rel_types():

    rel_ls = []
    rel_type_query = """CALL db.relationshipTypes()"""
    result = neo4j_utils.query(rel_type_query)
    for el in result:
        rel_ls.append(el[0])
    return rel_ls


def get_graph_list():

    graph_ls = []
    list_graph_query = """CALL gds.graph.list()"""
    existing_graphs = neo4j_utils.query(list_graph_query)
    if existing_graphs:
        for el in existing_graphs:
            graph_ls.append(el[1])
    return graph_ls

############################## 

st.sidebar.title('Graph management')

if st.sidebar.button('Get graph list'):
    graph_ls = get_graph_list()
    if len(graph_ls) > 0:
        for el in graph_ls:
            st.sidebar.write(el)
    else:
        st.sidebar.write('There are currently no graphs in memory.')

st.sidebar.markdown("""---""")

label_ls = get_node_labels()
source = st.sidebar.selectbox('Choose a source node type: ', label_ls)

rel_ls = get_rel_types()
rel = st.sidebar.selectbox('Choose a relationship type: ', rel_ls)

target = st.sidebar.selectbox('Choose a target node type: ', label_ls)

st.sidebar.markdown("""---""")

create_graph = st.sidebar.text_input('Name of graph to be created: ')
if st.sidebar.button('Create in-memory graph'):
    st.sidebar.write(source, target, rel)
    create_graph_query = """CALL gds.graph.create(
                                    '{}',
                                    ['{}', '{}'],
                                    '{}'
                            )
                         """.format(create_graph, source, target, rel)
    result = neo4j_utils.query(create_graph_query)
    st.sidebar.write('Graph ', result[0][2], 'has ', result[0][3], 'nodes and ', result[0][4],' relationships.')

st.sidebar.markdown("""---""")

drop_graph = st.sidebar.selectbox('Choose an graph to drop: ', get_graph_list())
if st.sidebar.button('Drop in-memory graph'):
    drop_graph_query = """CALL gds.graph.drop('{}')""".format(drop_graph)
    result = neo4j_utils.query(drop_graph_query)
    st.sidebar.write('Graph ', result[0][0],' has been dropped.')

st.sidebar.markdown("""---""")

##############################
#
#   Main panel content
#
##############################

def create_graph_df():

    df_query = """MATCH (n) RETURN n.name, n.frp_emb, n.n2v_emb"""
    df = pd.DataFrame([dict(_) for _ in neo4j_utils.query(df_query)])

    return df


def create_tsne_plot(emb_name='p.n2v_emb', n_components=2):

    tsne_query = """MATCH (p:Person) RETURN p.name AS name, p.death_year AS death_year, {} AS vec
    """.format(emb_name)
    df = pd.DataFrame([dict(_) for _ in neo4j_utils.query(tsne_query)])
    df['is_dead'] = np.where(df['death_year'].isnull(), 1, 0)
    #st.dataframe(df)

    X_emb = TSNE(n_components=n_components).fit_transform(list(df['vec']))

    tsne_df = pd.DataFrame(data = {
        'x': [value[0] for value in X_emb],
        'y': [value[1] for value in X_emb], 
        'label': df['is_dead']
    })

    return tsne_df

##############################


col1, col2 = st.beta_columns((1, 2))

#####
#
# Embedding column (col1)
#
#####

with col1:
    emb_graph = st.text_input('Enter graph name for embedding creation:')

    with st.beta_expander('FastRP embedding management'):
        st.markdown("Description of hyperparameters can be found [here](https://neo4j.com/docs/graph-data-science/current/algorithms/fastrp/#algorithms-embeddings-fastrp)")
        frp_dim = st.slider('FastRP embedding dimenson', value=4, min_value=2, max_value=50)
        frp_it_weight1 = st.slider('Iteration weight 1', value=0., min_value=0., max_value=1.)
        frp_it_weight2 = st.slider('Iteration weight 2', value=1., min_value=0., max_value=1.)
        frp_it_weight3 = st.slider('Iteration weight 3', value=1., min_value=0., max_value=1.)
        frp_norm = st.slider('FRP normalization strength', value=0., min_value=-1., max_value=1.)
        frp_seed = st.slider('Random seed', value=42, min_value=1, max_value=99)

        if st.button('Create FastRP embedding'):
            frp_query = """CALL gds.fastRP.write('%s', {
                            embeddingDimension: %d,
                            iterationWeights: [%f, %f, %f],
                            normalizationStrength: %f,
                            randomSeed: %d,
                            writeProperty: 'frp_emb'
            })
            """ % (emb_graph, frp_dim, frp_it_weight1, 
                   frp_it_weight2, frp_it_weight3, frp_norm, 
                   frp_seed)
            result = neo4j_utils.query(frp_query)

    with st.beta_expander('node2vec embedding creation'):
        st.markdown("Description of hyperparameters can be found [here](https://neo4j.com/docs/graph-data-science/current/algorithms/node2vec/)")
        n2v_dim = st.slider('node2vec embedding dimenson', value=4, min_value=2, max_value=50)
        n2v_walk_length = st.slider('Walk length', value=80, min_value=2, max_value=160)
        n2v_walks_node = st.slider('Walks per node', value=10, min_value=2, max_value=50)
        n2v_io_factor = st.slider('inOutFactor', value=1.0, min_value=0.001, max_value=1.0, step=0.05)
        n2v_ret_factor = st.slider('returnFactor', value=1.0, min_value=0.001, max_value=1.0, step=0.05)
        n2v_neg_samp_rate = st.slider('negativeSamplingRate', value=10, min_value=5, max_value=20)
        n2v_iterations = st.slider('Number of training iterations', value=1, min_value=1, max_value=10)
        n2v_init_lr = st.slider('Initial learning rate', value=0.01, min_value=0.001, max_value=0.1, step=0.01)
        n2v_min_lr = st.slider('Minimum learning rate', value=0.0001, min_value=0.0001, max_value=0.01, step=0.001)
        n2v_walk_bs = st.slider('Walk buffer size', value=1000, min_value=100, max_value=2000)
        n2v_seed = st.slider('Random seed:', value=42, min_value=1, max_value=99)

        if st.button('Create node2vec embedding'):
            n2v_query = """CALL gds.beta.node2vec.write('%s', {
                            embeddingDimension: %d,
                            walkLength: %d,
                            walksPerNode: %d,
                            inOutFactor: %f,
                            returnFactor: %f,
                            negativeSamplingRate: %d,
                            iterations: %d,
                            initialLearningRate: %f,
                            minLearningRate: %f,
                            walkBufferSize: %d,
                            randomSeed: %d,
                            writeProperty: 'n2v_emb'
            })
            """ % (emb_graph, n2v_dim, n2v_walk_length,
                   n2v_walks_node, n2v_io_factor, n2v_ret_factor,
                   n2v_neg_samp_rate, n2v_iterations, n2v_init_lr,
                   n2v_min_lr, n2v_walk_bs, n2v_seed)
            result = neo4j_utils.query(n2v_query)

    st.markdown("---")

    if st.button('Show embeddings'):
        df = create_graph_df()
        st.dataframe(df)

    if st.button('Drop embeddings'):
        neo4j_utils.query('MATCH (n) REMOVE n.frp_emb')
        neo4j_utils.query('MATCH (n) REMOVE n.n2v_emb')



with col2:
    st.header('t-SNE')

    plt_emb = st.selectbox('Choose an embedding to plot: ', ['FastRP', 'node2vec'])
    if plt_emb == 'FastRP':
        emb_name = 'p.frp_emb'
    else:
        emb_name = 'p.n2v_emb'

    if st.button('Plot embeddings'):

        tsne_df = create_tsne_plot(emb_name=emb_name)
        ch_alt = alt.Chart(tsne_df).mark_point().encode(
            x='x', 
            y='y', 
            color=alt.Color('label:O', scale=alt.Scale(range=['red', 'blue']))
        ).properties(width=800, height=800)
        st.altair_chart(ch_alt, use_container_width=True)




