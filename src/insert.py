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
        data_to_insert=[]
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
                data_to_insert.append({"name": employee["name"], "manager_id": supervisor["db_id"]})
 
        if len(data_to_insert)>0:
            print(f"    {employee_type} insertion...{len(data_to_insert)}")
            result= employee_dao.insert_many(data_to_insert)
            print(f"    {employee_type} insertion...OK")
            index=0
            for id in result:
                employees_payload.append({"id": data[index]["id"], "db_id": id})
                index=index+1
        
    return employees_payload


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

    driver.close()


if __name__ == "__main__":
    run()
