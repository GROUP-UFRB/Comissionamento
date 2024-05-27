import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import uvicorn
from fastapi import FastAPI
from models import Commission, User, Role
from contextlib import asynccontextmanager

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
    Identificar hierarquias com lacunas (ex.: hierarquias que não possuem um determinado nível como o RG, hierarquias sem RV, etc.)
    """
    try:
        query = (
            "MATCH (rm:RM) "
            "MATCH path = (rm)-[:MANAGES*]-(rv:RV) "
            "WHERE length(path) < 4 OR none(p IN nodes(path) WHERE 'RV' IN labels(p)) "
            "RETURN rm, path "
            "UNION "
            "MATCH (rm:RM) "
            "WHERE NOT EXISTS { MATCH (rm)-[:MANAGES*]-(rp1:RP1) } "
            "AND NOT EXISTS { MATCH (rm)-[:MANAGES*]-(rp2:RP2) } "
            "AND NOT EXISTS { MATCH (rm)-[:MANAGES*]-(rp3:RP3) } "
            "AND NOT EXISTS { "
            "    MATCH path = (rm)-[:MANAGES*]-(rv:RV) "
            "    WHERE length(path) = 4 AND any(p IN nodes(path) WHERE 'RV' IN labels(p)) "
            "} "
            "RETURN rm, NULL as path"
        )
        result = session.run(query)
        return result.data()
    except Exception as e:
        print(f"Erro: {e}")


@app.get("/compute_commission")
async def compute_commission(
    commission: Commission,
):
    """
    Calcular o comissionamento de um medicamento a partir do seu tipo e o seu valor bruto
    """
    # >>>>>> RETORNA O COMISSIONAMENTO DE ACORDO COM O TIPO DE MEDICAMENTO E COM A HIERARQUIA
    # MATCH path = (x)<-[:SUBORDINATED_TO*0..]-(:RV {name: "Arthur Brooks"}) RETURN x.sporadic_commission, labels(x)

    # >>>>>> RETORNA O COMISSIONAMENTO DE ACORDO COM O TIPO DE MEDICAMENTO
    # MATCH path = (x)<-[:SUBORDINATED_TO*0..]-()
    # WITH x, labels(x) AS label_list, x.continuous_commission AS commission
    # UNWIND label_list AS label
    # RETURN commission, COLLECT(DISTINCT label) AS unique_labels
    try:
        query = (
            "MATCH path = (x)<-[:SUBORDINATED_TO*0..]-()"
            f" WITH x, labels(x) AS label_list, x.{commission.type_commission} AS commission"
            " UNWIND label_list AS label"
            " RETURN commission, COLLECT(DISTINCT label) AS label"
        )
        result = session.run(query)

        data = {
            record["label"][0]: record["commission"] * commission.value
            for record in result
        }
        return data
    except Exception as e:
        print(f"Erro: {e}")


@app.delete("/reset_db", status_code=204)
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
