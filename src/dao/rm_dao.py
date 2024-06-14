class RmDao:

    def __init__(self, session) -> None:
        self.session = session

    def create(self, users):
        result = self.session.write_transaction(self._create_rm, users)
        return result

    @staticmethod
    def _create_rm(tx, users):
        query = "UNWIND $users AS user CREATE (rm:RM {name: user.name, id: randomUUID()}) RETURN rm.id AS node_id"
        result = tx.run(query, users=users)
        node_ids = []
        for record in result:
            node_ids.append(record["node_id"])
        return node_ids
