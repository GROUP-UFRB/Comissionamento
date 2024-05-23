class Rp2Dao:

    def __init__(self, session) -> None:
        self.session = session

    def create(self, name, manager_id):
        result = self.session.write_transaction(self._create_rp2, name, manager_id)
        return result

    @staticmethod
    def _create_rp2(tx, name, manager_id):
        query = ("CREATE (rp2:RP2 {name: $name, id: randomUUID()})"
                 "WITH rp2"
                 " MATCH (rm {id:$id})"
                 " CREATE (rp2)-[:SUBORDINATED_TO]->(rm)"
                 " CREATE (rm)-[:MANAGES]->(rp2)"
                 " RETURN rp2.id AS node_id"
                 )
        result = tx.run(query, name=name, id=manager_id)
        record = result.single()
        return record["node_id"]
