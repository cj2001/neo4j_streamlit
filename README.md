# neo4j_streamlit
### Written by: Dr. Clair J. Sullivan, Data Science Advocate, Neo4j
#### email: clair.sullivan@neo4j.com
#### Twitter: @CJLovesData1
#### Last updated: 2021-06-10

## Introduction

The purpose of this code is to demonstrate how to create a [Streamlit](https://streamlit.io) dashboard to be used for the visualization of embeddings created by the [Graph Data Science](https://dev.neo4j.com/graph_data_science) library in [Neo4j](https://dev.neo4j.com/neo4j).  This will hopefully be useful for developing an intuitive feel for these embeddings and how the different hyperparameters impact the overall results.

For more information on graph embeddings, you can read my blog post on [Getting Started with Graph Embeddings in Neo4j](https://dev.neo4j.com/intro_graph_emb_tds) in Towards Data Science (written in May, 2021).

## How to get started

1. Create a [Neo4j Sandbox](https://dev.neo4j.com/sandbox)
  - Select "Launch a Free Instance"
  - Select "New Project"
  - Choose "Graph Data Science": This will create an instance pre-populated with the Game of Thrones graph we will use to get started
  - Choose the drop-down on the right of the instance and select "Connection details"
  - Record the Bolt URL and Password
2. Build the Streamlit container
  - Edit the Dockerfile to include the Bolt URL and password from the previous step
  - From the root directory of this repo, type `docker build -t neo_stream .`
  - Once built, type `docker run -p 8501:8501 -v $PWD/src:/examples neo_stream`
3. Using a browser, navigate to the provided IP address
  - This typically will be something like `http://172.17.0.2:8501`
4. In the side panel, provide a name of the in-memory graph to be created and click "Create in-memory graph"
5. Have fun with the functionality in the main area of the dashboard!  How well can you tune the hyperparameters to get as much clustering separation between the living (blue) and the dead (red) characters???

**Note:** If you would like, you can navigate to `https://bolt.URL.address:7474` and you can interact with the graph directly via Cypher.

## Major caveats!!!

1. This is _very much_ a work in progress!  As such, there are only two types of graph embeddings included (FastRP and node2vec) and not all of the hyperparameters have been added yet.  Be sure to watch for future modifications and regularly pull the main branch of this repo to keep with the current version.
2. The in-memory graph that is created is only the undirected, monopartite graph `(Person)-[:INTERACTS]-(Person)`.  Future versions of this code will allow you to create additional graphs.
3. This is a very small graph!  It only has about 2600 nodes and not quite 17,000 relationships.  And we make that even smaller by limiting the nodes and relationships as described above.  Based on these facts, we do not expect the quality of the embeddings to be that great.  In future work, we will use a larger graph and discuss how to optimize embeddings.

