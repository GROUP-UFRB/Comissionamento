class Rp3Dao:

    def __init__(self, session) -> None:
        self.session = session

    def create(self, name, manager_id):
        result = self.session.write_transaction(self._create_rp3, name, manager_id)
        return result
    
    def insert_many(self, nodes):
        result = self.session.write_transaction(self._create_many_rp3, nodes)
        return result

    @staticmethod
    def _create_many_rp3(tx, nodes):
        query = (
            " UNWIND $nodes AS node"
            " CREATE (new:RP3 {name: node.name, id: randomUUID()})"
            " WITH new,node"
            " MATCH (root {id:node.manager_id})"
            " CREATE (new)-[:SUBORDINATED_TO]->(root)"
            " CREATE (root)-[:MANAGES]->(new)"
            " RETURN new.id AS node_id"
        )
        result = tx.run(query, nodes=nodes)
        node_ids = []
        for record in result:
            node_ids.append(record["node_id"])
        return node_ids

    @staticmethod
    def _create_rp3(tx, name, manager_id):
        query = ("CREATE (rp3:RP3 {name: $name, id: randomUUID()})"
                 "WITH rp3"
                 " MATCH (rm {id:$id})"
                 " CREATE (rp3)-[:SUBORDINATED_TO]->(rm)"
                 " CREATE (rm)-[:MANAGES]->(rp3)"
                 " RETURN rp3.id AS node_id"
                 )
        result = tx.run(query, name=name, id=manager_id)
        record = result.single()
        return record["node_id"]
