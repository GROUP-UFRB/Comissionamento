class RvDao:

    def __init__(self, session) -> None:
        self.session = session

    def create(self, name, manager_id):
        result = self.session.write_transaction(self._create_rv, name, manager_id)
        return result

    @staticmethod
    def _create_rv(tx, name, manager_id):
        query = (
            "CREATE (rv:RV {name: $name, id: randomUUID()})"
            "WITH rv"
            " MATCH (rc {id:$id})"
            " CREATE (rv)-[:SUBORDINATED_TO]->(rc)"
            " CREATE (rc)-[:MANAGES]->(rv)"
            " RETURN rv.id AS node_id"
        )
        result = tx.run(query, name=name, id=manager_id)
        record = result.single()
        return record["node_id"]
