import mysql.connector
import os

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
    )
# from mysql.connector import pooling
# import os
# from dotenv import load_dotenv

# load_dotenv()
# dbconfig = {
#     "host": os.getenv("DB_HOST"),
#     "port": os.getenv("DB_PORT"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASS"),
#     "database": os.getenv("DB_NAME"),
# }

# connection_pool = pooling.MySQLConnectionPool(
#     pool_name="composite_pool",
#     pool_size=5,
#     pool_reset_session=True,
#     **dbconfig
# )

# def get_db_connection():
#     return connection_pool.get_connection()
