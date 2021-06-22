import argparse

import numpy as np
import pandas as pd

import streamlit as st

from neo4j_utils import Neo4jConnection


parser = argparse.ArgumentParser(description='Add uri, user, and pwd for Neo4j connection.')
parser.add_argument('uri', type=str, default=None)
parser.add_argument('user', type=str, default='neo4j')
parser.add_argument('pwd', type=str, default=None)

args=parser.parse_args()

neo4j_utils = Neo4jConnection(uri=args.uri, user=args.user, pwd=args.pwd)

emb = 'FastRP'

##############################
#
#   Sidebar content
#
##############################

st.sidebar.title('Basic graph interface')

if st.sidebar.button('List existing graphs'):
    list_graph_query = """CALL gds.graph.list()"""
    result = neo4j_utils.query(list_graph_query)
    if result:
        for el in result:
            st.sidebar.write(el[1])
    else:
        st.sidebar.write('There are currently no graphs in memory.')

st.sidebar.markdown("""---""")

create_graph = st.sidebar.text_input('Name of graph to be created: ')
if st.sidebar.button('Create in-memory graph'):
    create_graph_query = """CALL gds.graph.create(
                                    '{}',
                                    '*',
                                    '*'
                            )
                         """.format(create_graph)

    result = neo4j_utils.query(create_graph_query)
    st.sidebar.write('Graph ', result[0][2], 'has ', result[0][3], 'nodes and ', result[0][4],' relationships.')

st.sidebar.markdown("""---""")

drop_graph = st.sidebar.text_input('Name of graph to be dropped: ')
if st.sidebar.button('Drop in-memory graph'):
    drop_graph_query = """CALL gds.graph.drop('{}')""".format(drop_graph)
    result = neo4j_utils.query(drop_graph_query)
    st.sidebar.write('Graph ', result[0][0],' has been dropped.')

st.sidebar.markdown("""---""")

emb = st.sidebar.selectbox('Choose an embedding: ', ['FastRP', 'node2vec'])

dim = st.sidebar.slider('Embedding dimension: ', value=10, min_value=2, max_value=50)

emb_graph = st.sidebar.text_input('Enter graph name for embedding creation:')

if st.sidebar.button('Create embeddings'):
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

if st.sidebar.button('Drop embeddings'):
    neo4j_utils.query('MATCH (n) REMOVE n.frp_emb')
    neo4j_utils.query('MATCH (n) REMOVE n.n2v_emb')

##############################
#
#   Main panel content
#
##############################

def create_df():

    df_query = """MATCH (n) RETURN n.name, n.frp_emb, n.n2v_emb"""
    df = pd.DataFrame([dict(_) for _ in neo4j_utils.query(df_query)])

    return df

if st.button('Show embeddings'):
    df = create_df()
    st.dataframe(df)




