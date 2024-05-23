class RcDao:

    def __init__(self, session) -> None:
        self.session = session

    def create(self,name,manager_id):
        result = self.session.write_transaction(self._create_rc, name, manager_id)
        return result

    @staticmethod
    def _create_rc(tx, name, manager_id):
        query = ("CREATE (rc:RC {name: $name, id: randomUUID()})"
                 "WITH rc"
                 " MATCH (rg {id:$id})"
                 " CREATE (rc)-[:SUBORDINATED_TO]->(rg)"
                 " CREATE (rg)-[:MANAGES]->(rc)"
                 " RETURN rc.id AS node_id"
                 )
        result = tx.run(query, name=name, id=manager_id)
        record = result.single()
        return record["node_id"]
