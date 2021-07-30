import pandas as pd
from neo4j import GraphDatabase

class Neo4jConnection:
    
    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
        
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
        
    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if session is not None:
                session.close()
        return response


class Neo4jInteractions:
    
    def __init__(self, uri, user, pwd):
        self.__conn = Neo4jConnection(uri=uri, user=user, pwd=pwd )
        try:
            res = self.__conn.query('MATCH (n) RETURN COUNT(n)')
        except Exception as e:
            print('Neo4jInteractions not properly created: ', e)
        

    def get_node_labels(self):
        
        label_ls = []
        label_type_query = """CALL db.labels()"""
        result = self.__conn.query(label_type_query)
        for el in result:
            #st.write(el[0])
            label_ls.append(el[0])
        return label_ls

    def get_rel_types(self):

        rel_ls = []
        rel_type_query = """CALL db.relationshipTypes()"""
        result = self.__conn.query(rel_type_query)
        for el in result:
            rel_ls.append(el[0])
        return rel_ls


    def get_graph_list(self):

        graph_ls = []
        list_graph_query = """CALL gds.graph.list()"""
        existing_graphs = self.__conn.query(list_graph_query)
        if existing_graphs:
            for el in existing_graphs:
                graph_ls.append(el[1])
        return graph_ls

    def create_graph(self, graph_name):

        create_graph_query = """CALL gds.graph.create(
                                    '%s', 
                                    'Person', 
                                    {
                                        INTERACTS_WITH: {
                                                type: 'INTERACTS',
                                                orientation: 'UNDIRECTED'
                                            }
                                    }
                                )
                            """ % (graph_name)
        result = self.__conn.query(create_graph_query)
        # Returns graph name, number of nodes, and number of edges
        return result[0][2], result[0][3], result[0][4]
    
    def drop_graph(self, graph_name):

        drop_graph_query = """CALL gds.graph.drop('{}')""".format(graph_name)
        result = self.__conn.query(drop_graph_query)
        return result[0][0]
    
    def create_graph_df(self, limit=None):

        if limit:
            df_query = """
                MATCH (n)
                RETURN n.name AS name, n.frp_emb, n.n2v_emb
                LIMIT %d
            """ % limit
        else:
            df_query = """MATCH (n) RETURN n.name, n.frp_emb, n.n2v_emb"""
        df = pd.DataFrame([dict(_) for _ in self.__conn.query(df_query)])

        return df
    
    def create_frp_embs(self, emb_graph, frp_dim, frp_it_weight1, 
                        frp_it_weight2, frp_it_weight3, frp_norm, frp_seed):
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
            result = self.__conn.query(frp_query)
            return

    def create_n2v_embs(self, emb_graph, n2v_dim, n2v_walk_length,
                        n2v_walks_node, n2v_io_factor, n2v_ret_factor,
                        n2v_neg_samp_rate, n2v_iterations, n2v_init_lr,
                        n2v_min_lr, n2v_walk_bs, n2v_seed):
        
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
        self.__conn.query(n2v_query)
            
        return


    def drop_embeddings(self, graph_name):

        self.__conn.query("""MATCH (n) REMOVE n.frp_emb""")
        self.__conn.query("""MATCH (n) REMOVE n.n2v_emb""")

        return
