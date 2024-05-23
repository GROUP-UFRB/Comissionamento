import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

DATABASE_URL = "bolt://localhost:7687"
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
AUTH = (USER, PASSWORD)

def get_all_hierarchy():  # Representar toda a hierarquia da empresa
    try:
        result = session.run(
            "MATCH path = (:RM)-[:SUBORDINATED_TO*]-(representante) RETURN path")
        return result.data()
    except Exception as e:
        print(f"Erro: {e}")


# Recuperar todos os subordinados de determinado profissional
def get_all_subordinates_of(type: str, name: str):
    try:
        query = f"MATCH path = (x)-[:SUBORDINATED_TO*]->(:{type} {name:'{name}'}) RETURN path"
        result = session.run(query)
        return result.data()
    except Exception as e:
        print(f"Erro: {e}")


# Recuperar a hierarquia superior de um profissional
def get_superior_hierarchy_of(type: str, name: str):
    try:
        query = f"MATCH path = (:{type} {name:{name}})-[:SUBORDINATED_TO*]->(result) RETURN result"
        result = session.run(query)
        return result.data()
    except Exception as e:
        print(f"Erro: {e}")

# Identificar hierarquias com lacunas (ex.: hierarquias que não possuem um determinado nível como o RG, hierarquias sem RV, etc.)
def get_hierarchy_with_fails():
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


def execute_query(query_key, session):
    try:
        result = session.run(QUERIES.get(query_key))
        return result.data()
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    try:
        driver = GraphDatabase.driver(DATABASE_URL, auth=AUTH)
        with driver.session() as session:
            while True:
                print("Consultas disponíveis:")
                for key, query in QUERIES.items():
                    print(f"{key}: {query}")

                selected_query = input(
                    "\nSelecione a chave da consulta que deseja executar (ou 'q' para sair): ")

                if selected_query.lower() == "q":
                    break

                if selected_query not in QUERIES:
                    print(
                        "Chave inválida. Por favor, selecione uma das consultas disponíveis.\n")
                    continue

                print(f"Executando consulta {selected_query}:")
                print(
                    f"\nResultado da consulta:\n{execute_query(selected_query, session)}\n")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        driver.close()
