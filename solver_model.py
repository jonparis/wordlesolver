import sqlite3


# noinspection SpellCheckingInspection
class MapsDB:

    def __init__(self):
        self.db_conn = sqlite3.connect('wordle.db')
        self.db_conn.execute(
            'CREATE TABLE IF NOT EXISTS KMAP (ID PRIMARY KEY NOT NULL, GUESS TEXT NOT NULL, AGTS FLOAT NOT NULL, CONFIDENCE INT DEFAULT 0, MATCHES INT NOT NULL DEFAULT 0, OPTIMIZED_TO INT NOT NULL DEFAULT 0);')
        self.db_conn.commit()

    def get_all_kmap(self):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT ID, GUESS, AGTS, CONFIDENCE, MATCHES, OPTIMIZED_TO FROM KMAP")
        all_kmaps = cursor.fetchall()
        if not all_kmaps: return {}
        kmap = {}
        for m in all_kmaps:
            if m: kmap[int(m[0])] = (m[1], m[2], m[3], m[4], m[5])
        return kmap

    # wip suggestion get/set
    def insert_knowledge(self, kint: int, guess: str, agts: float, confidence: int, matches: int, optimized_to: int):
        db_conn = self.db_conn
        db_conn.execute(
            "INSERT OR REPLACE INTO KMAP (ID, GUESS, CONFIDENCE, AGTS, MATCHES, OPTIMIZED_TO) VALUES ('" + str(kint) + "', '" + guess + "', " + str(confidence) + ", " + str(agts) + ", " + str(matches) + ", " + str(optimized_to) + ")")
        db_conn.commit()

    def get_knowledge(self, kint: int):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT GUESS, AGTS, CONFIDENCE, MATCHES OPTIMIZED_TO FROM KMAP WHERE ID = '" + str(kint) + "'")
        k = cursor.fetchone()
        if k:
            return {"g": k[0], "agts": k[1], "c": k[2], "m": k[3], "o": k[4]}
        else:
            return False

    def close_db(self):
        self.db_conn.close()
