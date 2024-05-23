class RgDao:

    def __init__(self, session) -> None:
        self.session = session

    def create(self,name,manager_id):
        result = self.session.write_transaction(self._create_rd, name, manager_id)
        return result

    @staticmethod
    def _create_rd(tx, name, manager_id):
        query = ("CREATE (rg:RG {name: $name, id: randomUUID()})"
             "WITH rg"
             " MATCH (rd {id:$id})"
             " CREATE (rg)-[:SUBORDINATED_TO]->(rd)"
             " CREATE (rd)-[:MANAGES]->(rg)"
             " RETURN rg.id AS node_id"
             )
        result = tx.run(query, name=name, id=manager_id)
        record = result.single()
        return record["node_id"]

