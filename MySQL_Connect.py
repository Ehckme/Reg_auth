import mysql.connector
# from sqlalchemy import create_engine

conn = mysql.connector.connect(host='localhost', user='root', password='root', )

if conn.is_connected():
    print('Connection Established')

my_cursor = conn.cursor()
my_cursor.execute('CREATE DATABASE New_User_Database')
my_cursor.execute('SHOW DATABASES')
for db in my_cursor:
    print(db)
# my_cursor.close()
# conn.close()