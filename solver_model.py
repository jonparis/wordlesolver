import sqlite3


# noinspection SpellCheckingInspection
class MapsDB:

    def __init__(self):
        self.db_conn = sqlite3.connect('wordle.db')
        self.db_conn.execute(
            'CREATE TABLE IF NOT EXISTS KMAP (ID PRIMARY KEY NOT NULL, GINT INT NOT NULL, PERFECT INT DEFAULT 0);')
        self.db_conn.commit()

    def get_all_kmap(self):
        db_conn = self.db_conn
        cursor = db_conn.execute("SELECT ID, GINT, PERFECT FROM KMAP")
        all_kmaps = cursor.fetchall()
        if not all_kmaps: return {}
        kmap = {}
        for m in all_kmaps:
            if m: kmap[int(m[0])] = (m[1], m[2])
        return kmap


    def purge_db(self):
        db_conn = self.db_conn
        self.db_conn.execute('DROP TABLE KMAP;')
        self.db_conn.commit()
        self.db_conn.execute('VACUUM;')
        self.db_conn.commit()
        self.db_conn.execute(
            'CREATE TABLE IF NOT EXISTS KMAP (ID PRIMARY KEY NOT NULL, GINT INT NOT NULL, PERFECT INT DEFAULT 0);')
        self.db_conn.commit()


    def insert_knowledge(self, kint: int, kmap: tuple):
        db_conn = self.db_conn
        db_conn.execute(
            "INSERT OR REPLACE INTO KMAP (ID, GINT, PERFECT) VALUES ('" + str(kint) + "', " + str(kmap[0]) + ", " + str(kmap[1]) + ")")
        db_conn.commit()
