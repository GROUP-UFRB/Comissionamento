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


def find_index(matrix, target):
    for i, row in enumerate(matrix):
        if target in row:
            return (i, row.index(target))
    return None


@app.get("/compute_commission")
async def compute_commission(commission: Commission):
    """
    Calcular o comissionamento de um medicamento a partir do seu tipo e o seu valor bruto
    """
    commissions = {
        "RM": {"continuous": 0.03, "sporadic": 0.06, "high_cost": 0.08},
        "RD": {"continuous": 0.04, "sporadic": 0.07, "high_cost": 0.09},
        "RP1": {"continuous": 0.20, "sporadic": 0.30, "high_cost": 0.40},
        "RP2": {"continuous": 0.25, "sporadic": 0.35, "high_cost": 0.50},
        "RP3": {"continuous": 0.34, "sporadic": 0.47, "high_cost": 0.69},
        "RG": {"continuous": 0.05, "sporadic": 0.08, "high_cost": 0.10},
        "RC": {"continuous": 0.10, "sporadic": 0.12, "high_cost": 0.20},
        "RV": {"continuous": 0.15, "sporadic": 0.20, "high_cost": 0.30},
    }

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
        hierarchy = []
        labels = []
        for record in result:
            path = record["path"]
            for node in path.nodes:
                label = list(node.labels)[0]
                hierarchy.append({"name": node["name"], "position": label})
                labels.append(label)

        default_roles = [
            ["RV", "RC", "RG", "RD", "RM"],
            ["RP1", "RM"],
            ["RP2", "RM"],
            ["RP3", "RM"],
        ]

        commissions_values = {}
        roles = default_roles[find_index(default_roles, labels[0])[0]]

        for label in labels:
            if label in commissions_values:
                hierarchy.pop(0)
                aux = commissions_values[label]

                commissions_values[label] = []
                commissions_values[label].append(aux)
                commissions_values[label].append(
                    {
                        "name": [
                            item["name"]
                            for item in hierarchy
                            if item["position"] == label
                        ][0],
                        "commission": 0.0,
                    }
                )
            else:
                while True:
                    role = roles.pop(0)
                    if label not in commissions_values:
                        commissions_values[label] = {
                            "name": [
                                item["name"]
                                for item in hierarchy
                                if item["position"] == label
                            ][0],
                            "commission": 0.0,
                        }

                    commissions_values[label]["commission"] += (
                        commissions[role][commission.type_commission] * commission.value
                    )
                    if role == label:
                        break
        return commissions_values
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
