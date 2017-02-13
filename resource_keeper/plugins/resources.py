# -*- coding:utf-8 -*-

import sys
import os
sys.path.append(os.pardir)
import db
from .lib import is_exist_resouce_type, is_exist_resouce
from slackbot.bot import respond_to


def get_resource_status(conn, ch, rtype, rname):
    cur = conn.cursor()
    cur.execute("""
        SELECT user
        FROM resources
        WHERE channel = ?
        AND type = ?
        AND name = ?
    """, (ch, rtype, rname))
    rows = cur.fetchall()
    cur.close()

    return rows[0][0]


@respond_to('^\s*list\s+(\w+)\s*$')
def list_resource(msg, rtype):
    ch = msg.channel._body['name']
    conn = db.get_conn()
    try:
        if not is_exist_resouce_type(conn, ch, rtype):
            msg.reply("Oops! There is no resource type:{} in this channel".format(rtype))
            return

        cur = conn.cursor()
        cur.execute("""
            SELECT
                name,
                user
            FROM resources
            WHERE channel = ?
            AND type = ?
        """, (ch, rtype))
        rlist = cur.fetchall()
        cur.close()
    except Exception:
        msg.reply("Error: Sorry but I can't show you resource type:{}'s resource list in this channel".format(rtype))
        return
    finally:
        conn.close()

    if len(rlist) <= 0:
        msg.reply("Oops! There is no resource type:{}'s resources in this channel".format(rtype))
    else:
        ret_msg_elements = []
        for r in rlist:
            rname = r[0]
            rstatus = "<@{}>".format(r[1]) if r[1] is not None else "unused"
            ret_msg_elements.append("{}\t{}".format(rname, rstatus))
        ret_msg = "\n```\n{}\n```".format("\n".join(ret_msg_elements))
        msg.reply(ret_msg)


@respond_to('^\s*add\s+(\w+)\s+(\w+)\s*$')
def add_resource(msg, rtype, rname):
    ch = msg.channel._body['name']
    conn = db.get_conn()
    try:
        if not is_exist_resouce_type(conn, ch, rtype):
            msg.reply("Oops! There is no resource type:{} in this channel".format(rtype))
            return

        if is_exist_resouce(conn, ch, rtype, rname):
            msg.reply("Oops! {} was already existed in resource type:{}".format(rname, rtype))
            return

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO resources (
                channel, type, name, updated
            ) VALUES (
                ?, ?, ?, datetime('now')
            )
        """, (ch, rtype, rname))
        cur.close()
    except Exception:
        conn.rollback()
        msg.reply("Error: {} is not added to resource type:{}".format(rname, rtype))
        return
    finally:
        conn.commit()
        conn.close()

    msg.reply("{} is added to resource type:{}".format(rname, rtype))


@respond_to('^\s*remove\s+(\w+)\s+(\w+)\s*$')
def remove_resource(msg, rtype, rname):
    ch = msg.channel._body['name']
    conn = db.get_conn()
    try:
        if not is_exist_resouce_type(conn, ch, rtype):
            msg.reply("Oops! There is no resource type:{} in this channel".format(rtype))
            return

        if not is_exist_resouce(conn, ch, rtype, rname):
            msg.reply("Oops! {} is not existed in resource type:{}".format(rname, rtype))
            return

        uid = get_resource_status(conn, ch, rtype, rname)
        if uid is not None:
            msg.reply("Oops! {} is used by <@{}> in resource type:{}".format(rname, uid, rtype))
            return

        cur = conn.cursor()
        cur.execute("""
            DELETE FROM resources
            WHERE channel = ?
            AND type = ?
            AND name = ?
        """, (ch, rtype, rname))
        cur.close()
    except Exception:
        conn.rollback()
        msg.reply("Error: {} is not removed from resource type:{}".format(rname, rtype))
        return
    finally:
        conn.commit()
        conn.close()

    msg.reply("{} is removed from resource type:{}".format(rname, rtype))


@respond_to('^\s*lock\s+(\w+)\s+(\w+)\s*$')
def lock_resource(msg, rtype, rname):
    ch = msg.channel._body['name']
    uid = msg.channel._body['creator']
    conn = db.get_conn()
    try:
        if not is_exist_resouce_type(conn, ch, rtype):
            msg.reply("Oops! There is no resource type:{} in this channel".format(rtype))
            return

        if not is_exist_resouce(conn, ch, rtype, rname):
            msg.reply("Oops! {} is not existed in resource type:{}".format(rname, rtype))
            return

        lock_uid = get_resource_status(conn, ch, rtype, rname)
        if lock_uid is not None:
            msg.reply("Oops! {} is used by <@{}> in resource type:{}".format(rname, uid, rtype))
            return

        cur = conn.cursor()
        cur.execute("""
            UPDATE resources
            SET user = ?
            WHERE channel = ?
            AND type = ?
            AND name = ?
        """, (uid, ch, rtype, rname))
        cur.close()
    except Exception:
        conn.rollback()
        msg.reply("Error: {} is not locked in resource type:{}".format(rname, rtype))
        return
    finally:
        conn.commit()
        conn.close()

    msg.reply("OK. You can use {} in resource type:{}".format(rname, rtype))


@respond_to('^\s*unlock\s+(\w+)\s+(\w+)\s*$')
def unlock_resource(msg, rtype, rname):
    ch = msg.channel._body['name']
    uid = msg.channel._body['creator']
    conn = db.get_conn()
    try:
        if not is_exist_resouce_type(conn, ch, rtype):
            msg.reply("Oops! There is no resource type:{} in this channel".format(rtype))
            return

        if not is_exist_resouce(conn, ch, rtype, rname):
            msg.reply("Oops! {} is not existed in resource type:{}".format(rname, rtype))
            return

        lock_uid = get_resource_status(conn, ch, rtype, rname)
        if lock_uid is None:
            msg.reply("Oops! {} is not used already in resource type:{}".format(rname, rtype))
            return
        elif lock_uid != uid:
            msg.reply("Oops! {} is used by <@{}> in resource type:{}. You don't have permission.".format(rname, lock_uid, rtype))
            return

        cur = conn.cursor()
        cur.execute("""
            UPDATE resources
            SET user = NULL
            WHERE channel = ?
            AND type = ?
            AND name = ?
        """, (ch, rtype, rname))
        cur.close()
    except Exception:
        conn.rollback()
        msg.reply("Error: {} is not unlocked in resource type:{}".format(rname, rtype))
        return
    finally:
        conn.commit()
        conn.close()

    msg.reply("OK. I'll release {} in resource type:{}".format(rname, rtype))


@respond_to('^\s*force_unlock\s+(\w+)\s+(\w+)\s*$')
def force_unlock_resource(msg, rtype, rname):
    ch = msg.channel._body['name']
    conn = db.get_conn()
    try:
        if not is_exist_resouce_type(conn, ch, rtype):
            msg.reply("Oops! There is no resource type:{} in this channel".format(rtype))
            return

        if not is_exist_resouce(conn, ch, rtype, rname):
            msg.reply("Oops! {} is not existed in resource type:{}".format(rname, rtype))
            return

        lock_uid = get_resource_status(conn, ch, rtype, rname)
        if lock_uid is None:
            msg.reply("Oops! {} is not used already in resource type:{}".format(rname, rtype))
            return

        cur = conn.cursor()
        cur.execute("""
            UPDATE resources
            SET user = NULL
            WHERE channel = ?
            AND type = ?
            AND name = ?
        """, (ch, rtype, rname))
        cur.close()
    except Exception:
        conn.rollback()
        msg.reply("Error: {} is not unlocked in resource type:{}".format(rname, rtype))
        return
    finally:
        conn.commit()
        conn.close()

    msg.reply("OK. I'll release {} in resource type:{} by force".format(rname, rtype))
