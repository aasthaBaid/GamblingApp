import mysql.connector
from mysql.connector import Error

from db.settings import *

def create_connection():
    connection = None
    try:
       
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


create_connection()