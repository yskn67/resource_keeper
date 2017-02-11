# -*- coding:utf-8 -*-

import sys
import os
sys.path.append(os.pardir)
import db
from slackbot.bot import respond_to


class IsExistException(BaseException):
    pass


@respond_to('^\s*list\s*$')
def list_resource_type(msg):
    ch = msg.channel._body['name']
    conn = db.get_conn()
    try:
        ok = True
        cur = conn.cursor()
        cur.execute("""
            SELECT type
            FROM resource_types
            WHERE channel = ?
        """, (ch,))
        rtlist = cur.fetchall()
        cur.close()
    except Exception:
        conn.rollback()
        ok = False
    finally:
        conn.commit()
        conn.close()

    if not ok:
        msg.reply("Error: Sorry but I can't show you resouce type list in this channel")
    elif len(rtlist) <= 0:
        msg.reply("There is no resouce type in this channel")
    else:
        ret_msg = "\n```\n{}\n```".format("\n".join([rt[0] + "," for rt in rtlist]))
        msg.reply(ret_msg)


@respond_to('^\s*add\s+(\w+)\s*$')
def add_resource_type(msg, rtype):
    ch = msg.channel._body['name']
    conn = db.get_conn()
    try:
        exist = False
        ok = True
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
            raise(IsExistException("resource type is existed!"))

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO resource_types (
                channel, type
            ) VALUES (
                ?, ?
            )
        """, (ch, rtype))
        cur.close()
    except IsExistException:
        exist = True
    except Exception:
        conn.rollback()
        ok = False
    finally:
        conn.commit()
        conn.close()

    if exist:
        msg.reply("{} was already added to resource type".format(rtype))
    elif ok:
        msg.reply("{} is added to resource type".format(rtype))
    else:
        msg.reply("Error: {} is not added to resource type".format(rtype))


@respond_to('^\s*remove\s+(\w+)\s*$')
def remove_resource_type(msg, rtype):
    ch = msg.channel._body['name']
    conn = db.get_conn()
    try:
        exist = True
        ok = True
        cur = conn.cursor()
        cur.execute("""
            SELECT count(*)
            FROM resource_types
            WHERE channel = ?
            AND type = ?
        """, (ch, rtype))
        rows = cur.fetchall()
        cur.close()

        if rows[0][0] <= 0:
            raise(IsExistException("resource type is not existed!"))

        cur = conn.cursor()
        cur.execute("""
            DELETE FROM resource_types
            WHERE channel = ?
            AND type = ?
        """, (ch, rtype))
        cur.close()
    except IsExistException:
        exist = False
    except Exception:
        conn.rollback()
        ok = False
    finally:
        conn.commit()
        conn.close()

    if not exist:
        msg.reply("{} is not existed in resource type".format(rtype))
    elif ok:
        msg.reply("{} is removed from resource type".format(rtype))
    else:
        msg.reply("Error: {} is not removed from resource type".format(rtype))
