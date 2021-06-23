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

############################## 

st.sidebar.title('Graph management')

list_graph_query = """CALL gds.graph.list()"""
existing_graphs = neo4j_utils.query(list_graph_query)
if existing_graphs:
    for el in existing_graphs:
        st.sidebar.write('Existing in-memory graphs:')
        st.sidebar.write(el[1])
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

drop_graph = st.sidebar.text_input('Name of graph to be dropped: ')
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
        frp_dim = st.slider('FastRP embedding dimenson', value=4, min_value=2, max_value=50)
        frp_it_weight1 = st.slider('Iteration weight 1', value=0., min_value=0., max_value=1.)
        frp_it_weight2 = st.slider('Iteration weight 2', value=1., min_value=0., max_value=1.)
        frp_it_weight3 = st.slider('Iteration weight 3', value=1., min_value=0., max_value=1.)
        frp_norm = st.slider('FRP normalization strength', value=0., min_value=-1., max_value=1.)
        frp_seed = st.text_input('Random seed (int):')

        if st.button('Create FastRP embedding'):
            emb_query = """CALL gds.fastRP.write('%s', {
                            embeddingDimension: %d,
                            iterationWeights: [%f, %f, %f],
                            normalizationStrength: %f,
                            randomSeed: %d,
                            writeProperty: 'frp_emb'
            })
            """ % (emb_graph, frp_dim, frp_it_weight1, frp_it_weight2, frp_it_weight3, frp_norm, int(frp_seed))
            result = neo4j_utils.query(emb_query)
            st.write(emb_query)

    with st.beta_expander('Embedding management'):
        emb = st.selectbox('Choose an embedding to create: ', ['FastRP', 'node2vec'])
        dim = st.slider('Embedding dimension: ', value=10, min_value=2, max_value=50)
        #emb_graph = st.text_input('Enter graph name for embedding creation:')

        if st.button('Create embeddings'):
            if emb == 'FastRP':
                emb_query = """CALL gds.fastRP.write('%s', {
                                embeddingDimension: %d, 
                                writeProperty: 'frp_emb'}
                            )""" % (emb_graph, dim)
                result = neo4j_utils.query(emb_query)

            elif emb == 'node2vec':
                emb_query = """CALL gds.beta.node2vec.write('%s', { 
                                embeddingDimension: %d, 
                                writeProperty: 'n2v_emb'} 
                            )""" % (emb_graph, dim)
                result = neo4j_utils.query(emb_query)

            else:
                st.write('No embedding method selected')

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
        )
        st.altair_chart(ch_alt, use_container_width=True)




