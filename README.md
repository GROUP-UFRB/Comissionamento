# Neo4J

# Banco de Dados para Comissionamento Multi-Nível em Empresa Farmacêutica

Banco de dados para engoblar a estruturação do time comercial de uma empresa farmacêutica, caracterizada por uma hierarquia multi-nível. Dividida em duas carreiras - Representante Gestor e Representante Protagonista - cada uma com suas próprias regras de comissionamento, nossa solução modela toda a hierarquia da empresa, permitindo a recuperação dos subordinados de um profissional, a identificação de lacunas na hierarquia e a verificação de sua consistência. Além disso, o banco de dados realiza o cálculo do comissionamento de medicamentos com base em seu tipo e valor bruto, e impede modificações que violem a hierarquia estabelecida, garantindo sua integridade.

## Use virtual enviroment:

To enable virtual env ,if you not have virtualenv,use this comand for install:

```shell
 pip install virtualenv
```

And for enable use this:

```shell
 virtualenv env
 . env/bin/activate
```

## Install Dependecies:

```shell
pip install -r requirements.txt
```

## Run DB:

```shell
 docker-compose up -d
```

## Generate data:

```shell
python src/data/generate_data.py <args>
```

## Insert data

```shell
python src/insert.py
```

## Query utils

```shell
MATCH (n) DETACH DELETE n ## DELETE ALL DATA
MATCH (n) RETURN n ## SHOW ALL DATA
```

## Define neo4j credentials:

Create an `.env` file based on `.env.example` and define your credentials.
