# -*- coding: utf-8 -*-


def is_exist_resouce_type(conn, ch, rtype):
    cur = conn.cursor()
    cur.execute("""
        SELECT count(*)
        FROM resource_types
        WHERE channel = ?
        AND type = ?
    """, (ch, rtype))
    rows = cur.fetchall()
    cur.close()

    if rows[0][0] >= 1:
        return True
    else:
        return False


def is_exist_resouce(conn, ch, rtype, rname):
    cur = conn.cursor()
    cur.execute("""
        SELECT count(*)
        FROM resources
        WHERE channel = ?
        AND type = ?
        AND name = ?
    """, (ch, rtype, rname))
    rows = cur.fetchall()
    cur.close()

    if rows[0][0] >= 1:
        return True
    else:
        return False
