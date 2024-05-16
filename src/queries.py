import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

DATABASE_URL = "bolt://localhost:7687"
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
AUTH = (USER, PASSWORD)

QUERIES = {
    "11": "MATCH path = (:RM)-[:SUBORDINATED_TO*]-(representante) RETURN path",
    "21": "MATCH path = (x)-[:SUBORDINATED_TO]->(:RG {name:'Robert Carson'}) RETURN x",
    "22": "MATCH path = (x)-[:SUBORDINATED_TO*]->(:RG {name:'Robert Carson'}) RETURN path",
    "31": "MATCH path = (:RC {name:'Edward Ramirez'})-[:SUBORDINATED_TO*]->(representante) RETURN representante",
    # "41": "",
    # "51": "",
    # "61": "",
}


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

                selected_query = input("\nSelecione a chave da consulta que deseja executar (ou 'q' para sair): ")

                if selected_query.lower() == "q":
                    break

                if selected_query not in QUERIES:
                    print("Chave inválida. Por favor, selecione uma das consultas disponíveis.\n")
                    continue

                print(f"Executando consulta {selected_query}:")
                print(f"\nResultado da consulta:\n{execute_query(selected_query, session)}\n")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        driver.close()
