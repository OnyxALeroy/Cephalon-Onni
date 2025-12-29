import os
import psycopg2

from pymongo import MongoClient
from sqlalchemy import create_engine

# PostgreSQL with Apache AGE
POSTGRES_URI = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
sql_engine = create_engine(POSTGRES_URI)

# For AGE operations, use direct psycopg2 connection
age_conn = psycopg2.connect(
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    database=os.getenv('POSTGRES_DB'),
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT')
)

# MongoDB
mongo_client = MongoClient(os.getenv("MONGO_URI"))
