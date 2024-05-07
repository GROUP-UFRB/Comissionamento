from neo4j import GraphDatabase
import json


uri = "bolt://localhost:7687"
AUTH = ("neo4j", "U3z3W839YndB")


def _create_rm_node(tx, name):
    query = ("CREATE (n:RM {name: $name, id: randomUUID()}) "
             "RETURN n.id AS node_id")
    result = tx.run(query, name=name)
    record = result.single()
    return record["node_id"]


def _create_rp_node(tx, name, rm_id):
    query = ("CREATE (rv:RV {name: $name, id: randomUUID()})"
             "WITH rv"
             " MATCH (rm {id:$id})"
             " CREATE (rv)-[:SUBORDINATED_TO]->(rm)"
             " RETURN rv.id AS node_id"
             )
    result = tx.run(query, name=name, id=rm_id)
    record = result.single()
    return record["node_id"]


def _create_rd_node(tx, name, rm_id):
    query = ("CREATE (rd:RD {name: $name, id: randomUUID()})"
             "WITH rd"
             " MATCH (rm {id:$id})"
             " CREATE (rd)-[:SUBORDINATED_TO]->(rm)"
             " RETURN rd.id AS node_id"
             )
    result = tx.run(query, name=name, id=rm_id)
    record = result.single()
    return record["node_id"]


def _create_rg_node(tx, name, rm_id):
    query = ("CREATE (rg:RG {name: $name, id: randomUUID()})"
             "WITH rg"
             " MATCH (rd {id:$id})"
             " CREATE (rg)-[:SUBORDINATED_TO]->(rd)"
             " RETURN rg.id AS node_id"
             )
    result = tx.run(query, name=name, id=rm_id)
    record = result.single()
    return record["node_id"]


def _create_rc_node(tx, name, rm_id):
    query = ("CREATE (rc:RC {name: $name, id: randomUUID()})"
             "WITH rc"
             " MATCH (rg {id:$id})"
             " CREATE (rc)-[:SUBORDINATED_TO]->(rg)"
             " RETURN rc.id AS node_id"
             )
    result = tx.run(query, name=name, id=rm_id)
    record = result.single()
    return record["node_id"]


def _create_rv_node(tx, name, rm_id):
    query = ("CREATE (rv:RV {name: $name, id: randomUUID()})"
             "WITH rv"
             " MATCH (rc {id:$id})"
             " CREATE (rv)-[:SUBORDINATED_TO]->(rc)"
             " RETURN rv.id AS node_id"
             )
    result = tx.run(query, name=name, id=rm_id)
    record = result.single()
    return record["node_id"]


def insert_all_rms(session):
    with open('sample/rm.json') as file:
        data = json.load(file)
        rms_payload = []
        for item in data:
            id = session.execute_write(_create_rm_node, item["name"])
            rms_payload.append({
                "id": item["id"],
                "db_id": id
            })
    return rms_payload


def insert_all_rps(session, rms):
    with open('sample/rp.json') as file:
        data = json.load(file)
        rps_payload = []
        for rp in data:
            rm = next(
                (item for item in rms if item["id"] == rp["subordinateOf"]), False)
            if rm:
                id = session.execute_write(
                    _create_rp_node, rp["name"], rm["db_id"])
                rps_payload.append({
                    "id": rp["id"],
                    "db_id": id
                })
    return rps_payload


def insert_all_rds(session, rms):
    with open('data/rd.json') as file:
        data = json.load(file)
        rds_payload = []
        for rd in data:
            rm = next(
                (item for item in rms if item["id"] == rd["subordinateOf"]), False)
            if rm:
                id = session.execute_write(
                    _create_rd_node, rd["name"], rm["db_id"])
                rds_payload.append({
                    "id": rd["id"],
                    "db_id": id
                })
    return rds_payload


def insert_all_rgs(session, rds):
    with open('sample/rg.json') as file:
        data = json.load(file)
        rgs_payload = []
        for rg in data:
            rd = next(
                (item for item in rds if item["id"] == rg["subordinateOf"]), False)
            if rd:
                id = session.execute_write(
                    _create_rg_node, rg["name"], rd["db_id"])
                rgs_payload.append({
                    "id": rg["id"],
                    "db_id": id
                })
    return rgs_payload


def insert_all_rcs(session, rgs):
    with open('sample/rc.json') as file:
        data = json.load(file)
        rcs_payload = []
        for rc in data:
            rg = next(
                (item for item in rgs if item["id"] == rc["subordinateOf"]), False)
            if rg:
                id = session.execute_write(
                    _create_rc_node, rc["name"], rg["db_id"])
                rcs_payload.append({
                    "id": rc["id"],
                    "db_id": id
                })
    return rcs_payload


def insert_all_rvs(session, rcs):
    with open('sample/rv.json') as file:
        data = json.load(file)
        rvs_payload = []
        for rv in data:
            rc = next(
                (item for item in rcs if item["id"] == rv["subordinateOf"]), False)
            if rc:
                id = session.execute_write(
                    _create_rv_node, rv["name"], rc["db_id"])
                rvs_payload.append({
                    "id": rv["id"],
                    "db_id": id
                })
    return rvs_payload


def run():
    driver = GraphDatabase.driver(uri, auth=AUTH)
    with driver.session() as session:
        rms = insert_all_rms(session)
        insert_all_rps(session, rms)
        rds = insert_all_rds(session, rms)
        rgs = insert_all_rgs(session, rds)
        rcs = insert_all_rcs(session, rgs)
        rvs = insert_all_rvs(session, rcs)

    driver.close()


if __name__ == "__main__":
    run()