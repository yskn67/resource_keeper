# -*- coding:utf-8 -*-

import sys
import os
sys.path.append(os.pardir)
import db
from .lib import is_exist_resouce_type
from slackbot.bot import respond_to


@respond_to('^\s*list\s*$')
def list_resource_type(msg):
    ch = msg.channel._body['name']
    conn = db.get_conn()
    try:
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
        msg.reply("Error: Sorry but I can't show you resource type list in this channel")
        return
    finally:
        conn.commit()
        conn.close()

    if len(rtlist) <= 0:
        msg.reply("Oops! There is no resource type in this channel")
    else:
        ret_msg = "\n```\n{}\n```".format("\n".join([rt[0] for rt in rtlist]))
        msg.reply(ret_msg)


@respond_to('^\s*add\s+(\w+)\s*$')
def add_resource_type(msg, rtype):
    ch = msg.channel._body['name']
    conn = db.get_conn()
    try:
        if is_exist_resouce_type(conn, ch, rtype):
            msg.reply("Oops! {} was already existed in resource type".format(rtype))
            return

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO resource_types (
                channel, type
            ) VALUES (
                ?, ?
            )
        """, (ch, rtype))
        cur.close()
    except Exception:
        conn.rollback()
        msg.reply("Error: {} is not added to resource type".format(rtype))
        return
    finally:
        conn.commit()
        conn.close()

    msg.reply("{} is added to resource type".format(rtype))


@respond_to('^\s*remove\s+(\w+)\s*$')
def remove_resource_type(msg, rtype):
    ch = msg.channel._body['name']
    conn = db.get_conn()
    try:
        if not is_exist_resouce_type(conn, ch, rtype):
            msg.reply("Oops! {} is not existed in resource type".format(rtype))
            return

        cur = conn.cursor()
        cur.execute("""
            DELETE FROM resource_types
            WHERE channel = ?
            AND type = ?
        """, (ch, rtype))
        cur.close()

        cur = conn.cursor()
        cur.execute("""
            DELETE FROM resources
            WHERE channel = ?
            AND type = ?
        """, (ch, rtype))
        cur.close()
    except Exception:
        conn.rollback()
        msg.reply("Error: {} is not removed from resource type".format(rtype))
        return
    finally:
        conn.commit()
        conn.close()

    msg.reply("{} is removed from resource type".format(rtype))
