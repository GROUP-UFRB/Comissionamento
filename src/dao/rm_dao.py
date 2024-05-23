
class RmDao:
      
    def __init__(self, session) -> None:
        self.session = session

    def create(self, name):
        result = self.session.write_transaction(self._create_rm, name)
        return result

    @staticmethod
    def _create_rm(tx, name):
        query = ("CREATE (n:RM {name: $name, id: randomUUID()}) "
                 "RETURN n.id AS node_id")
        result = tx.run(query, name=name)
        record = result.single()
        return record["node_id"]
