import sqlite3
import sys
import traceback
import uuid
import hashlib
import os
from Crypto.Cipher import AES


class KDCServer():
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
            sqlite_create_table_query = '''CREATE TABLE chat_room (
                                        
                                        roomId BLOB Not Null,
                                        messages TEXT,
                                        roomName TEXT Not Null

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

    def insertUser( roomId,messages,roomName):
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(BASE_DIR, "SQLite_Python.db")
            sqliteConnection = sqlite3.connect(db_path)
            cursor = sqliteConnection.cursor()
            print("Successfully Connected to SQLite")
            challangeFromServer = uuid.uuid1().bytes
            print(roomId,messages,roomName)
            sqlite_insert_query = """INSERT INTO chat_room
                                  (roomId,messages,roomName)  VALUES  (?, ?,?)"""

            count = cursor.execute(sqlite_insert_query, (roomId, messages,roomName))
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
        cur.execute("SELECT * FROM chat_room")

        rows = cur.fetchall()
        print("sdfsdfsdfds")
        for row in rows:
            print("888")
            print(row)

    def getRoomIdForClient(roomName):
        print("getRoomIdForClient")
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "SQLite_Python.db")

        sqliteConnection = sqlite3.connect(db_path)
        cur = sqliteConnection.cursor()

        cur.execute("SELECT * FROM chat_room WHERE roomname=?", (roomName,))

        rows = cur.fetchall()
        roomId=""
        print(len(rows) == 0,"rowssssssssssssssssssssss")
        if len(rows)!= 0:
            print("not none ---------------------")
            for row in rows:
                roomId = row[0]
                print(roomId)
        else:
            print("put uuid +++++++++++++++")
            roomId =  hashlib.sha256(roomName.encode()).digest()
            print("before",roomId)
            KDCServer.insertUser(roomId, "none", roomName)



        return roomId

    def getRoomId(roomName,sessionId):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "SQLite_Python.db")

        sqliteConnection = sqlite3.connect(db_path)
        cur = sqliteConnection.cursor()

        cur.execute("SELECT * FROM chat_room WHERE roomName=?", (roomName,))

        rows = cur.fetchall()

        for row in rows:
            roomId = row[0]




        #Encrypted the room Id with the session ID
        iv = b'Sixteen byte key'
        obj2 = AES.new(roomId, AES.MODE_CFB, iv)
        msg = obj2.encrypt(sessionId)

        return msg

KDCServer.createDB(KDCServer)
KDCServer.createTable(KDCServer)