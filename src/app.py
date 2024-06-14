import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import uvicorn
from fastapi import FastAPI
from models import Commission, User, Role
from contextlib import asynccontextmanager
from commission import ComputeCommission

load_dotenv()

DATABASE_URL = "bolt://localhost:7687"
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
AUTH = (USER, PASSWORD)
PORT = int(os.getenv("PORT") or 8000)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global session
    driver = GraphDatabase.driver(DATABASE_URL, auth=AUTH)
    session = driver.session()

    yield

    driver.close()


app = FastAPI(lifespan=lifespan)


@app.get("/get_all_based_on_role")
async def get_all_based_on_role(role: Role):
    """
    Listar todos com base no cargo
    """
    try:
        query = f"MATCH (n:{role.role}) RETURN n.name as name, n.id as id"
        result = session.run(query, role=role.role)
        return result.data()
    except Exception as e:
        print(f"Erro: {e}")


@app.get("/get_all_hierarchy")
async def get_all_hierarchy():
    """
    Representar toda a hierarquia da empresa
    """
    try:
        result = session.run(
            "MATCH path = (:RM)-[:SUBORDINATED_TO*]-(representante) RETURN path"
        )

        return result.data()
    except Exception as e:
        print(f"Erro: {e}")


@app.get("/get_all_subordinates_of")
async def get_all_subordinates_of(
    user: User,
):
    """
    Recuperar todos os subordinados de determinado profissional
    """
    try:
        query = (
            f"MATCH path = (x)-[:SUBORDINATED_TO*]->(:{user.role}"
            "{name:"
            f"'{user.name}'"
            "}) RETURN path"
        )
        result = session.run(query)
        return result.data()
    except Exception as e:
        print(f"Erro: {e}")


@app.get("/get_superior_hierarchy_of")
async def get_superior_hierarchy_of(
    user: User,
):
    """
    Recuperar a hierarquia superior de um profissional
    """
    try:
        query = (
            f"MATCH path = (:{user.role}"
            "{name:"
            f"'{user.name}'"
            "})-[:SUBORDINATED_TO*]->(result) RETURN result"
        )
        result = session.run(query)
        return result.data()
    except Exception as e:
        print(f"Erro: {e}")


@app.get("/get_hierarchy_with_fails")
async def get_hierarchy_with_fails():
    """
    Identificar hierarquias com lacunas
    Exemplo :
    - Hierarquias sem o RD,RG,RC mas com RV
    - Nós sem relação alguma
    - RM sem RV e RP1,RP2,RP3
    - Hierarquias sem RM
    """
    try:
        query = (
            " MATCH (root:RM)"
            " OPTIONAL MATCH  path0 = (root)-[:MANAGES*]-(rv:RV) "
            " OPTIONAL MATCH  path1 = (root)-[:MANAGES*]-(rp1:RP1) "
            " OPTIONAL MATCH  path2 = (root)-[:MANAGES*]-(rp2:RP2) "
            " OPTIONAL MATCH  path3 = (root)-[:MANAGES*]-(rp3:RP3) "
            " with root,path0,path1,path2,path3"
            " WHERE length(path0) < 4 OR none(p IN nodes(path0) WHERE 'RV' IN labels(p)) "
            " OR (path0 is NULL AND path1 is NULL AND path2 is NULL AND path3 is NULL)"
            " return root,path0 as path"
            " UNION"
            " MATCH (root)"
            " WHERE NOT (root)--()"
            " RETURN root,NULL as path"
            " UNION"
            " MATCH (root)"
            " MATCH path = (root)-[:SUBORDINATED_TO]-(result) "
            " WHERE none(p IN nodes(path) WHERE 'RM' IN labels(p))"
            " AND NOT EXISTS {"
            " MATCH path1=(root)-[:SUBORDINATED_TO*]->(rm:RM)"
            " return path1"
            " }"
            " return root, path"
        )
        result = session.run(query)
        return result.data()
    except Exception as e:
        print(f"Erro: {e}")


@ app.get("/compute_commission")
async def compute_commission(commission: Commission):
    """
    Calcular o comissionamento de um medicamento a partir do seu tipo e o seu valor bruto
    """
    try:
        query = (
            f"MATCH path = (:{commission.user.role}"
            "{name:"
            f"'{commission.user.name}'"
            "})-[:SUBORDINATED_TO*0..]->(:RM) RETURN path"
        )
        result = session.run(query)
        if not result.peek():
            return "No user was found with the characteristics reported. Check the information and try again!"

        return ComputeCommission.compute_commission(result, commission)
    except Exception as e:
        print(f"Erro: {e}")


@ app.delete("/reset_db", status_code=204)
async def reset_db():
    """
    Limpar o banco de dados
    """
    try:
        session.run("match ( n ) detach delete n")
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    uvicorn.run(app, port=PORT)
