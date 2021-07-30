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
