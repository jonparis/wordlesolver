import sqlite3
import json

class MapsDB:

    def __init__(self):
        self.db_conn = sqlite3.connect('wordle.db')

        # stable solver
        self.db_conn.execute('CREATE TABLE IF NOT EXISTS SMAP_TABLE (ID PRIMARY KEY NOT NULL, SUGGESTION TEXT);')
        # WIP solver
        self.db_conn.execute('CREATE TABLE IF NOT EXISTS SUGGESTIONS (ID PRIMARY KEY NOT NULL, SUGGESTION TEXT NOT NULL);')
        self.db_conn.execute('CREATE TABLE IF NOT EXISTS KMAP (ID PRIMARY KEY NOT NULL, GUESS TEXT NOT NULL, AGTS FLOAT NOT NULL);')

    # stable suggestion get/set
    def insert_suggestion(self, k_hash, suggestion):
        db_conn = self.db_conn
        db_conn.execute("INSERT OR REPLACE INTO SMAP_TABLE (ID,SUGGESTION) VALUES ('" + k_hash + "', '" + suggestion + "')")
        db_conn.commit()

    def get_suggestion(self, k_hash):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT SUGGESTION FROM SMAP_TABLE WHERE ID = '" + k_hash + "'")
        suggestion = cursor.fetchone()
        if suggestion:
            return suggestion[0]
        else:
            return False

    # wip suggestion get/set
    def insert_suggestion2(self, k_hash, suggestion):
        db_conn = self.db_conn
        db_conn.execute("INSERT OR REPLACE INTO SUGGESTIONS (ID,SUGGESTION) VALUES ('" + k_hash + "', '" + suggestion + "')")
        db_conn.commit()

    def get_suggestion2(self, k_hash):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT SUGGESTION FROM SUGGESTIONS WHERE ID = '" + k_hash + "'")
        suggestion = cursor.fetchone()
        if suggestion:
            return suggestion[0]
        else:
            return False

    def insert_Knowledge(self, k_hash, guess, agts):
        try:
            db_conn = self.db_conn
            db_conn.execute("INSERT OR REPLACE INTO KMAP (ID,GUESS,AGTS) VALUES ('" + k_hash + "', '" + guess + "', " + str(agts) + ")")
            db_conn.commit()
        except: 
            print("db connection issue in insert Knowledge")

    def get_Knowledge(self, k_hash):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT GUESS, AGTS FROM KMAP WHERE ID = '" + k_hash + "'")
        k = cursor.fetchone()
        if k:
            return {"g" : k[0], "c" : k[1]}
        else:
            return False

    def close_db(self):
        self.db_conn.close()
