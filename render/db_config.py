import os

# env variables stored in Render (PaaS) 
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')

# analytical db hosted on AWS RDS
source_database = {
    "dbname": "analyticaldb",
    "user": DB_USER,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "port": "5432",
}