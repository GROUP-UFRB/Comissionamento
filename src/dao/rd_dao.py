class RdDao:

    def __init__(self, session) -> None:
        self.session = session

    def create(self, name, manager_id):
        result = self.session.write_transaction(
            self._create_rd, name, manager_id)
        return result

    def insert_many(self, nodes):
        result = self.session.write_transaction(self._create_many_rd, nodes)
        return result

    @staticmethod
    def _create_many_rd(tx, nodes):
        query = (
            " UNWIND $nodes AS node"
            " CREATE (rd:RD {name: node.name, id: randomUUID()})"
            " WITH rd,node"
            " MATCH (rm {id:node.manager_id})"
            " CREATE (rd)-[:SUBORDINATED_TO]->(rm)"
            " CREATE (rm)-[:MANAGES]->(rd)"
            " RETURN rd.id AS node_id"
        )
        result = tx.run(query, nodes=nodes)
        node_ids = []
        for record in result:
            node_ids.append(record["node_id"])
        return node_ids
    @staticmethod
    def _create_rd(tx, name, manager_id):
        query = ("CREATE (rd:RD {name: $name, id: randomUUID()})"
                 "WITH rd"
                 " MATCH (rm {id:$id})"
                 " CREATE (rd)-[:SUBORDINATED_TO]->(rm)"
                 " CREATE (rm)-[:MANAGES]->(rd)"
                 " RETURN rd.id AS node_id"
                 )
        result = tx.run(query, name=name, id=manager_id)
        record = result.single()
        return record["node_id"]
