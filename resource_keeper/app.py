# -*- coding: utf-8 -*-

import sys
import db
from slackbot.bot import Bot


def create_table():
    conn = db.get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resource_types (
                channel TEXT NOT NULL,
                type TEXT NOT NULL,
                PRIMARY KEY(channel, type)
            )
            """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                channel TEXT NOT NULL,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                user TEXT,
                updated DATETIME NOT NULL,
                PRIMARY KEY(channel, type)
            )
            """)
        ok = True
    except Exception:
        conn.rollback()
        ok = False
    finally:
        cur.close()
        conn.commit()
        conn.close()

    return ok


def main():
    ok = create_table()
    if not ok:
        print("Resource table is not created!", file=sys.stderr)
        sys.exit(1)
    bot = Bot()
    print("start resource keeper")
    bot.run()


if __name__ == '__main__':
    main()
