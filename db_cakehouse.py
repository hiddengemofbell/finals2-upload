import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # XAMPP default = empty
    database="db_cakehouse"
)

cursor = conn.cursor()