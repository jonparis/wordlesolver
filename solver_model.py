import sqlite3


# noinspection SpellCheckingInspection
class MapsDB:

    def __init__(self):
        self.db_conn = sqlite3.connect('wordle.db')
        self.db_conn.execute(
            'CREATE TABLE IF NOT EXISTS KMAP (ID PRIMARY KEY NOT NULL, GINT INT NOT NULL, PERFECT INT DEFAULT 0);')
        self.db_conn.commit()

    def get_all_kmap(self, hard: bool):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT ID, GINT, PERFECT FROM KMAP")
        all_kmaps = cursor.fetchall()
        if not all_kmaps: return {}
        kmap = {}
        for m in all_kmaps:
            m = list(m)
            if hard:
                if m[0][0] == "h":
                    m[0] = m[0][1:]
                else:
                    continue
            elif m[0][0] == "h":
                continue
            kmap[int(m[0])] = (m[1], m[2])
        return kmap

    def purge_db(self, hard: bool):
        db_conn = self.db_conn
        if hard:
            db_conn.execute("DELETE FROM KMAP WHERE ID LIKE 'h%'")
        else:
            db_conn.execute("DELETE FROM KMAP WHERE ID NOT LIKE 'h%'")
        self.db_conn.commit()
        self.db_conn.execute('VACUUM;')
        self.db_conn.commit()

    def insert_knowledge(self, kint: int, kmap: tuple, hard: bool):
        db_conn = self.db_conn
        skint = str(kint)
        if hard: skint = "h" + skint
        db_conn.execute(
            "INSERT OR REPLACE INTO KMAP (ID, GINT, PERFECT) VALUES ('" + skint + "', " + str(kmap[0]) + ", " + str(
                kmap[1]) + ")")
        db_conn.commit()
