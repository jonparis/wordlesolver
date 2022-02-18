import json
import sqlite3


# noinspection SpellCheckingInspection
class MapsDB:

    def __init__(self):
        self.db_conn = sqlite3.connect('wordle.db')
        self.db_conn.execute('CREATE TABLE IF NOT EXISTS SUGGESTIONS (ID PRIMARY KEY NOT NULL, SUGGESTION TEXT);')
        self.db_conn.execute(
            'CREATE TABLE IF NOT EXISTS KMAP (ID PRIMARY KEY NOT NULL, GUESS TEXT NOT NULL, AGTS FLOAT NOT NULL, CONFIDENCE INT DEFAULT 0);')
        self.db_conn.commit()

    def get_all_kmap(self):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT ID, GUESS, AGTS, CONFIDENCE FROM KMAP")
        all_kmaps = cursor.fetchall()
        if not all_kmaps: return {}
        kmap = {}
        for m in all_kmaps:
            if m: kmap[m[0]] = (m[1], m[2], m[3])
        return kmap

    # stable suggestion get/set
    def insert_suggestion(self, k_hash: str, suggestion: str):
        db_conn = self.db_conn
        db_conn.execute(
            "INSERT OR REPLACE INTO SUGGESTIONS (ID,SUGGESTION) VALUES ('" + k_hash + "', '" + suggestion + "')")
        db_conn.commit()

    def get_suggestion(self, k_hash: str):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT SUGGESTION FROM SUGGESTIONS WHERE ID = '" + k_hash + "'")
        suggestion = cursor.fetchone()
        if suggestion:
            return suggestion[0]
        else:
            return False

    # wip suggestion get/set
    def insert_knowledge(self, k_hash: str, guess: str, agts: float, confidence: int):
        db_conn = self.db_conn
        db_conn.execute(
            "INSERT OR REPLACE INTO KMAP (ID, GUESS, CONFIDENCE, AGTS) VALUES ('" + k_hash + "', '" + guess + "', " + str(confidence) + ", " + str(agts) + ")")
        db_conn.commit()

    def get_knowledge(self, k_hash: str):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT GUESS, AGTS, CONFIDENCE FROM KMAP WHERE ID = '" + k_hash + "'")
        k = cursor.fetchone()
        if k:
            return {"g": k[0], "agts": k[1], "c": k[2]}
        else:
            return False

    def close_db(self):
        self.db_conn.close()
