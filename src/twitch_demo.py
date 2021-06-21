import numpy as np
import pandas as pd

import streamlit as st

from neo4j_utils import Neo4jConnection

neo4j_utils = Neo4jConnection(uri='bolt://3.231.58.8:7687', 
                              user='neo4j',
                              pwd='band-thermometer-sash')

st.sidebar.title('Basic graph interface')

emb = 'FastRP'

##############################
#
#   Sidebar content
#
##############################

if st.sidebar.button('List existing graphs'):
    list_graph_query = """CALL gds.graph.list()"""
    result = neo4j_utils.query(list_graph_query)
    if result:
        for el in result:
            st.sidebar.write(el[1])
    else:
        st.sidebar.write('There are currently no graphs in memory.')

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

drop_graph = st.sidebar.text_input('Name of graph to be dropped: ')
if st.sidebar.button('Drop in-memory graph'):
    drop_graph_query = """CALL gds.graph.drop('{}')""".format(drop_graph)
    result = neo4j_utils.query(drop_graph_query)
    st.sidebar.write('Graph ', result[0][0],' has been dropped.')

emb = st.sidebar.selectbox('Choose an embedding: ', ['FastRP', 'node2vec'])

dim = st.sidebar.slider('Embedding dimension: ', value=10, min_value=2, max_value=50)

emb_graph = st.sidebar.text_input('Enter graph name for embedding creation:')

if st.sidebar.button('Create embeddings'):
    if emb == 'FastRP':
        emb_query = """CALL gds.fastRP.write('%s', {
                          embeddingDimension: 10, 
                          writeProperty: 'frp_all_nodes'}
                    )""" % (emb_graph)
        result = neo4j_utils.query(emb_query)
    else:
        st.write('No embs created')

##############################
#
#   Main panel content
#
##############################






