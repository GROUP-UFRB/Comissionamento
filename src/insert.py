import os
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase
from dao.rc_dao import RcDao
from dao.rd_dao import RdDao
from dao.rg_dao import RgDao
from dao.rm_dao import RmDao
from dao.rp1_dao import Rp1Dao
from dao.rp2_dao import Rp2Dao
from dao.rp3_dao import Rp3Dao

load_dotenv()

DATABASE_URL = "bolt://localhost:7687"
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
AUTH = (USER, PASSWORD)
DATA_PATH = os.getenv('DATA_PATH', "sample")


def insert_all_rms(session):
    rm_dao = RmDao(session)
    with open(f"{DATA_PATH}/rm.json") as file:
        data = json.load(file)
        rms_payload = []
        for item in data:
            id = rm_dao.create(item["name"])
            rms_payload.append({
                "id": item["id"],
                "db_id": id
            })
    return rms_payload


def insert_all_rps1(session, rms):
    rp1_dao = Rp1Dao(session)
    with open(f"{DATA_PATH}/rp1.json") as file:
        data = json.load(file)
        rps_payload = []
        for rp in data:
            rm = next(
                (item for item in rms if item["id"] == rp["subordinateOf"]), False)
            if rm:
                id = rp1_dao.create(rp["name"], rm["db_id"])
                rps_payload.append({
                    "id": rp["id"],
                    "db_id": id
                })
    return rps_payload


def insert_all_rps2(session, rms):
    rp2_dao = Rp2Dao(session)
    with open(f'{DATA_PATH}/rp2.json') as file:
        data = json.load(file)
        rps_payload = []
        for rp in data:
            rm = next(
                (item for item in rms if item["id"] == rp["subordinateOf"]), False)
            if rm:
                id = rp2_dao.create(rp["name"], rm["db_id"])
                rps_payload.append({
                    "id": rp["id"],
                    "db_id": id
                })
    return rps_payload


def insert_all_rps3(session, rms):
    rp3_dao = Rp3Dao(session)
    with open(f'{DATA_PATH}/rp3.json') as file:
        data = json.load(file)
        rps_payload = []
        for rp in data:
            rm = next(
                (item for item in rms if item["id"] == rp["subordinateOf"]), False)
            if rm:
                id = rp3_dao.create(rp["name"], rm["db_id"])
                rps_payload.append({
                    "id": rp["id"],
                    "db_id": id
                })
    return rps_payload


def insert_all_rds(session, rms):
    rd_dao = RdDao(session)
    with open(f'{DATA_PATH}/rd.json') as file:
        data = json.load(file)
        rds_payload = []
        for rd in data:
            rm = next(
                (item for item in rms if item["id"] == rd["subordinateOf"]), False)
            if rm:
                id = rd_dao.create(rd["name"], rm["db_id"])
                rds_payload.append({
                    "id": rd["id"],
                    "db_id": id
                })
    return rds_payload


def insert_all_rgs(session, rds):
    rd_dao = RdDao(session)
    with open(f'{DATA_PATH}/rg.json') as file:
        data = json.load(file)
        rgs_payload = []
        for rg in data:
            rd = next(
                (item for item in rds if item["id"] == rg["subordinateOf"]), False)
            if rd:
                id = rd_dao.create(rg["name"], rd["db_id"])
                rgs_payload.append({
                    "id": rg["id"],
                    "db_id": id
                })
    return rgs_payload


def insert_all_rcs(session, rgs):
    rg_dao = RgDao(session)
    with open(f'{DATA_PATH}/rc.json') as file:
        data = json.load(file)
        rcs_payload = []
        for rc in data:
            rg = next(
                (item for item in rgs if item["id"] == rc["subordinateOf"]), False)
            if rg:
                id = rg_dao.create(rc["name"], rg["db_id"])
                rcs_payload.append({
                    "id": rc["id"],
                    "db_id": id
                })
    return rcs_payload


def insert_all_rvs(session, rcs):
    rc_dao = RcDao(session)
    with open(f'{DATA_PATH}/rv.json') as file:
        data = json.load(file)
        rvs_payload = []
        for rv in data:
            rc = next(
                (item for item in rcs if item["id"] == rv["subordinateOf"]), False)
            if rc:
                id = rc_dao.create(rv["name"], rc["db_id"])
                rvs_payload.append({
                    "id": rv["id"],
                    "db_id": id
                })
    return rvs_payload


def run():
    driver = GraphDatabase.driver(DATABASE_URL, auth=AUTH)
    print("Start insertion...")
    with driver.session() as session:
        rms = insert_all_rms(session)
        print(" RM insertion...Ok")
        insert_all_rps1(session, rms)
        print(" RP1 insertion...Ok")
        insert_all_rps2(session, rms)
        print(" RP2 insertion...Ok")
        insert_all_rps3(session, rms)
        print(" RP3 insertion...Ok")
        rds = insert_all_rds(session, rms)
        print(" RDS insertion...Ok")
        rgs = insert_all_rgs(session, rds)
        print(" RGS insertion...Ok")
        rcs = insert_all_rcs(session, rgs)
        print(" RCS insertion...Ok")
        rvs = insert_all_rvs(session, rcs)
        print(" RVS insertion...Ok")
        print(">>>Insertion Finished!<<<")

    driver.close()


if __name__ == "__main__":
    run()
