import os

from neo4j import GraphDatabase
from pymongo import MongoClient
from sqlalchemy import create_engine

# Postgres
POSTGRES_URI = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
sql_engine = create_engine(POSTGRES_URI)

# MongoDB
mongo_client = MongoClient(os.getenv("MONGO_URI"))

# Neo4j
neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)
