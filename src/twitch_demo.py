import numpy as np
import pandas as pd

import streamlit as st

from neo4j_utils import Neo4jConnection

neo4j_utils = Neo4jConnection(uri='bolt://3.231.58.8:7687', 
                              user='neo4j',
                              pwd='band-thermometer-sash')

st.sidebar.title('Basic graph interface')

emb = 'FastRP'

emb = st.sidebar.selectbox('Choose an embedding: ', ['FastRP', 'node2vec'])
st.write('You selected: ', emb)

dim = st.sidebar.slider('Embedding dimension: ', value=10, min_value=2, max_value=50)
st.write('We will use ', dim, ' dimensions for the ', emb, ' embedding.')

num_nodes = neo4j_utils.query('MATCH(n) RETURN COUNT(n)')

st.write('Nodes in graph: ', num_nodes[0][0])

if st.button('Create df'):
    query = """MATCH (p:Person)-[:BELONGS_TO]->(h:House)
               RETURN p.name AS name, h.name AS house
               ORDER BY h.name, p.name"""
    df = pd.DataFrame([dict(_) for _ in neo4j_utils.query(query)])
    st.dataframe(df.style.hide_index())

if st.button('Create in-memory graph'):
    create_graph_query = """CALL gds.graph.create(
                                    'all',
                                    '*',
                                    '*'
                            )
                         """

    result = neo4j_utils.query(create_graph_query)
    st.write(result)

if st.button('Drop in-memory graph'):
    drop_graph_query = """CALL gds.graph.drop('all')"""
    result = neo4j_utils.query(drop_graph_query)
    st.write(result)


