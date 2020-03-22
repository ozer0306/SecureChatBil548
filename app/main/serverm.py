import sqlite3
import sys
import traceback
import uuid
import hashlib
import os
from Crypto.Cipher import AES


class ServerM():
    def createDB(self):
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(BASE_DIR, "SQLite_Python.db")
            sqliteConnection = sqlite3.connect(db_path)
            cursor = sqliteConnection.cursor()
            print("Database created and Successfully Connected to SQLite")

            sqlite_select_Query = "select sqlite_version();"
            cursor.execute(sqlite_select_Query)
            record = cursor.fetchall()
            print("SQLite Database Version is: ", record)
            cursor.close()

        except sqlite3.Error as error:
            print("Error while connecting to sqlite", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The SQLite connection is closed")

    def createTable(self):
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(BASE_DIR, "SQLite_Python.db")
            sqliteConnection = sqlite3.connect(db_path)
            sqlite_create_table_query = '''CREATE TABLE user_authentication (
                                        username TEXT PRIMARY KEY,
                                        password BLOB Not Null,
                                        challange BLOB Not Null

                                         );'''

            cursor = sqliteConnection.cursor()
            print("Successfully Connected to SQLite")
            cursor.execute(sqlite_create_table_query)
            sqliteConnection.commit()
            print("SQLite table created")

            cursor.close()

        except sqlite3.Error as error:
            print("Error while creating a sqlite table", error)
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("sqlite connection is closed")

    def insertUser(usr, psd):
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(BASE_DIR, "SQLite_Python.db")
            sqliteConnection = sqlite3.connect(db_path)
            cursor = sqliteConnection.cursor()
            print("Successfully Connected to SQLite")
            challangeFromServer = uuid.uuid1().bytes
            sqlite_insert_query = """INSERT INTO user_authentication
                                  (username, password,challange)  VALUES  (?, ?, ?)"""

            count = cursor.execute(sqlite_insert_query, (usr, psd, challangeFromServer))
            sqliteConnection.commit()
            print("Record inserted successfully into SqliteDb_developers table ", cursor.rowcount)
            cursor.close()

            return challangeFromServer

        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table")
            print("Exception class is: ", error.__class__)
            print("Exception is", error.args)
            print('Printing detailed SQLite exception traceback: ')
            exc_type, exc_value, exc_tb = sys.exc_info()
            print(traceback.format_exception(exc_type, exc_value, exc_tb))
        finally:
            if (sqliteConnection):
                sqliteConnection.close()
                print("The SQLite connection is closed")

    def getAllUser(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "SQLite_Python.db")

        sqliteConnection = sqlite3.connect(db_path)
        cur = sqliteConnection.cursor()
        cur.execute("SELECT * FROM user_authentication")

        rows = cur.fetchall()
        print("sdfsdfsdfds")
        for row in rows:
            print("888")
            print(row)

    def getEncrytedMessage(encryptedMessage, userName):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "SQLite_Python.db")

        sqliteConnection = sqlite3.connect(db_path)
        cur = sqliteConnection.cursor()

        cur.execute("SELECT * FROM user_authentication WHERE username=?", (userName,))

        rows = cur.fetchall()

        for row in rows:
            hashPass = row[1]
            challange = row[2]
            print(row[1])

        iv = b'Sixteen byte key'
        obj2 = AES.new(hashPass, AES.MODE_CFB, iv)
        msg = obj2.encrypt(challange)

        print(encryptedMessage)
        print(msg)

        if encryptedMessage == msg:
            return True
        return False
ServerM.createDB(ServerM)
ServerM.createTable(ServerM)