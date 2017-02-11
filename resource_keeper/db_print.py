# -*- coding: utf-8

import db


conn = db.get_conn()

cur = conn.cursor()
cur.execute("SELECT * FROM resource_types")
print("resource_types:")
for row in cur.fetchall():
    print("\t".join([str(r) for r in row]))
cur.close()

cur = conn.cursor()
cur.execute("SELECT * FROM resources")
print("resources:")
for row in cur.fetchall():
    print("\t".join([str(r) for r in row]))
cur.close()

conn.close()
