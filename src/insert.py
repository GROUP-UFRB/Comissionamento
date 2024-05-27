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
    query = (
        "MATCH (rm:RM)"
        " MATCH (rd:RD)"
        " MATCH (rp1:RP1)"
        " MATCH (rp2:RP2)"
        " MATCH (rp3:RP3)"
        " MATCH (rg:RG)"
        " MATCH (rc:RC)"
        " MATCH (rv:RV)"
        " SET rm.continuous_commission = 0.03, rm.sporadic_commission = 0.06, rm.high_cost_commission = 0.08"
        " SET rd.continuous_commission = 0.04, rd.sporadic_commission = 0.07, rd.high_cost_commission = 0.09"
        " SET rp1.continuous_commission = 0.20, rp1.sporadic_commission = 0.30, rp1.high_cost_commission = 0.40"
        " SET rp2.continuous_commission = 0.25, rp2.sporadic_commission = 0.35, rp2.high_cost_commission = 0.50"
        " SET rp3.continuous_commission = 0.34, rp3.sporadic_commission = 0.47, rp3.high_cost_commission = 0.69"
        " SET rg.continuous_commission = 0.05, rg.sporadic_commission = 0.08, rg.high_cost_commission = 0.10"
        " SET rc.continuous_commission = 0.10, rc.sporadic_commission = 0.12, rc.high_cost_commission = 0.20"
        " SET rv.continuous_commission = 0.15, rv.sporadic_commission = 0.20, rv.high_cost_commission = 0.30"
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
