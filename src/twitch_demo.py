import numpy as np
import pandas as pd

import streamlit as st

from neo4j_utils import Neo4jConnection

neo4j_utils = Neo4jConnection(uri='bolt://3.231.58.8:7687', 
                              user='neo4j',
                              pwd='band-thermometer-sash')

st.sidebar.title('Basic graph interface')

emb = 'FastRP'

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

emb = st.sidebar.selectbox('Choose an embedding: ', ['FastRP', 'node2vec'])
st.write('You selected: ', emb)

dim = st.sidebar.slider('Embedding dimension: ', value=10, min_value=2, max_value=50)
st.write('We will use ', dim, ' dimensions for the ', emb, ' embedding.')



num_nodes = neo4j_utils.query('MATCH(n) RETURN COUNT(n)')

st.write('Nodes in graph: ', num_nodes[0][0])

# create_graph = st.text_input('Name of graph to be created: ')
# if st.button('Create in-memory graph'):
#     create_graph_query = """CALL gds.graph.create(
#                                     '{}',
#                                     '*',
#                                     '*'
#                             )
#                          """.format(create_graph)

#     st.write(create_graph_query)
#     result = neo4j_utils.query(create_graph_query)
#     st.write(result)

drop_graph = st.text_input('Name of graph to be dropped: ')
if st.button('Drop in-memory graph'):
    drop_graph_query = """CALL gds.graph.drop('{}')""".format(drop_graph)
    result = neo4j_utils.query(drop_graph_query)
    st.write(result)


