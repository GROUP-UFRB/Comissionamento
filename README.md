# Neo4J

# Banco de Dados para Comissionamento Multi-Nível em Empresa Farmacêutica

Banco de dados para englobar a estruturação do time comercial de uma empresa farmacêutica, caracterizada por uma hierarquia multi-nível. Dividida em duas carreiras - Representante Gestor e Representante Protagonista - cada uma com suas próprias regras de comissionamento, nossa solução modela toda a hierarquia da empresa, permitindo a recuperação dos subordinados de um profissional, a identificação de lacunas na hierarquia e a verificação de sua consistência. Além disso, o banco de dados realiza o cálculo do comissionamento de medicamentos com base em seu tipo e valor bruto, e impede modificações que violem a hierarquia estabelecida, garantindo sua integridade.

## Use virtual environment

To enable virtual env ,if you not have virtualenv,use this command for install:

```shell
 pip install virtualenv
```

And for enable use this:

```shell
 virtualenv env
 . env/bin/activate
```

## Install Dependencies

```shell
pip install -r requirements.txt
```

## Run DB

```shell
 docker-compose up -d
```

## Generate data

```shell
python src/data/generate_data.py <args>
```

or

```shell
python src/data/generate_and_insert_data.py
```

## Insert data

```shell
python src/insert.py
```

## Query utils

```shell
MATCH (n) DETACH DELETE n ## DELETE ALL DATA
MATCH (n) RETURN n ## SHOW ALL DATA
MATCH (a) WHERE id(a) = 54  DETACH DELETE a ## 
```

## Set information to run

Create an `.env` file based on `.env.example` and define its information.


## Run API

```shell
python src/app.py 
```

## View documentation about queries

`http://127.0.0.1:PORT/docs` or `http://127.0.0.1:PORT/redoc`
