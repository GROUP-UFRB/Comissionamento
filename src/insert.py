import os
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase
from dao.rv_dao import RvDao
from dao.rc_dao import RcDao
from dao.rd_dao import RdDao
from dao.rg_dao import RgDao
from dao.rm_dao import RmDao
from dao.rp1_dao import Rp1Dao
from dao.rp2_dao import Rp2Dao
from dao.rp3_dao import Rp3Dao

load_dotenv()

DATABASE_URL = "bolt://localhost:7687"
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
AUTH = (USER, PASSWORD)
DATA_PATH = os.getenv("DATA_PATH", "sample")


def insert_all_rms(session):
    rm_dao = RmDao(session)
    with open(f"{DATA_PATH}/rm.json") as file:
        data = json.load(file)
        rms_payload = []
        ids = rm_dao.create(data)
        for i, item in enumerate(data):
            rms_payload.append({"id": item["id"], "db_id": ids[i]})
    return rms_payload


def insert_all_employees(session, supervisors, employee_type):
    dao_mapping = {
        "rp1": Rp1Dao,
        "rp2": Rp2Dao,
        "rp3": Rp3Dao,
        "rd": RdDao,
        "rg": RgDao,
        "rc": RcDao,
        "rv": RvDao,
    }

    employee_dao = dao_mapping[employee_type](session)

    with open(f"{DATA_PATH}/{employee_type}.json") as file:
        data = json.load(file)
        employees_payload = []
        for employee in data:
            supervisor = next(
                (
                    item
                    for item in supervisors
                    if item["id"] == employee["subordinateOf"]
                ),
                False,
            )
            if supervisor:
                id = employee_dao.create(employee["name"], supervisor["db_id"])
                employees_payload.append({"id": employee["id"], "db_id": id})
    return employees_payload


def set_commission(session):
    commissions = [
        ("RM", 0.03, 0.06, 0.08),
        ("RD", 0.04, 0.07, 0.09),
        ("RP1", 0.20, 0.30, 0.40),
        ("RP2", 0.25, 0.35, 0.50),
        ("RP3", 0.34, 0.47, 0.69),
        ("RG", 0.05, 0.08, 0.10),
        ("RC", 0.10, 0.12, 0.20),
        ("RV", 0.15, 0.20, 0.30),
    ]

    for label, continuous, sporadic, high_cost in commissions:
        query = (
            f"MATCH (n: {label}) "
            f"SET n.continuous_commission = {continuous}, "
            f"n.sporadic_commission = {sporadic}, "
            f"n.high_cost_commission = {high_cost} "
        )
        session.run(query)


def run():
    driver = GraphDatabase.driver(DATABASE_URL, auth=AUTH)
    print("Start insertion...")
    with driver.session() as session:
        rms = insert_all_rms(session)
        print(" RM insertion...Ok")
        insert_all_employees(session, rms, "rp1")
        print(" RP1 insertion...Ok")
        insert_all_employees(session, rms, "rp2")
        print(" RP2 insertion...Ok")
        insert_all_employees(session, rms, "rp3")
        print(" RP3 insertion...Ok")
        rds = insert_all_employees(session, rms, "rd")
        print(" RDS insertion...Ok")
        rgs = insert_all_employees(session, rds, "rg")
        print(" RGS insertion...Ok")
        rcs = insert_all_employees(session, rgs, "rc")
        print(" RCS insertion...Ok")
        insert_all_employees(session, rcs, "rv")
        print(" RVS insertion...Ok")
        print(">>>Insertion Finished!<<<")
        print("\nStarting commissioning insertion...")
        set_commission(session)
        print(">>>Commissioning insertion completed!<<<")

    driver.close()


if __name__ == "__main__":
    run()
