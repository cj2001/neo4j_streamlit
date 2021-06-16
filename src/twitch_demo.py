import numpy
import pandas

import graphistry
import networkx
import streamlit as st

graphistry.register(api=3, protocol="https", server="hub.graphistry.com", 
                    token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImNqIiwiaWF0IjoxNjIzNjkyODM3LCJleHAiOjE2MjM2OTY0MzcsImp0aSI6IjkzNDgwODQzLTBlZjUtNDZlMC1iOTUyLTY3YTUwMmJmNjgzMyIsInVzZXJfaWQiOjE4ODksIm9yaWdfaWF0IjoxNjIzNjkyODM3fQ.6tI92r3bMOilIFCvCaELcaHPtch4T24O6cWDfXFQSxs"
                    )

st.sidebar.title('Basic graph interface')

emb = 'FastRP'

emb = st.sidebar.selectbox('Choose an embedding: ', ['FastRP', 'node2vec'])
st.write('You selected: ', emb)

dim = st.sidebar.slider('Embedding dimension: ', value=10, min_value=2, max_value=50)
st.write('We will use ', dim, ' dimensions for the ', emb, ' embedding.')

G = nx.complete_graph(100)


