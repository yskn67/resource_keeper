# -*- coding:utf-8 -*-

import sys
import os
sys.path.append(os.pardir)
import db
from .lib import IsExistException, IsNotExistException, IsLockedException, IsUnlockedException
from slackbot.bot import respond_to


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
        ok = True
        rtype_exist = True

        if not is_exist_resouce_type(conn, ch, rtype):
            raise(IsNotExistException("resource type is not existed!"))

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
    except IsNotExistException:
        rtype_exist = False
    except Exception:
        ok = False
    finally:
        conn.close()

    if not ok:
        msg.reply("Error: Sorry but I can't show you {}'s resouce list in this channel".format(rtype))
    elif not rtype_exist:
        msg.reply("There is no resouce type:{} in this channel".format(rtype))
    elif len(rlist) <= 0:
        msg.reply("There is no {}'s resouces in this channel".format(rtype))
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
        ok = True
        rtype_exist = True
        rname_exist = False

        if not is_exist_resouce_type(conn, ch, rtype):
            raise(IsNotExistException("resource type is not existed!"))

        if is_exist_resouce(conn, ch, rtype, rname):
            raise(IsExistException("resource is existed!"))

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO resources (
                channel, type, name, updated
            ) VALUES (
                ?, ?, ?, datetime('now')
            )
        """, (ch, rtype, rname))
        cur.close()
    except IsNotExistException:
        rtype_exist = False
    except IsExistException:
        rname_exist = True
    except Exception as e:
        print(e)
        conn.rollback()
        ok = False
    finally:
        conn.commit()
        conn.close()

    if not rtype_exist:
        msg.reply("There is no resouce type:{} in this channel".format(rtype))
    elif rname_exist:
        msg.reply("{} was already added to resouce type:{}".format(rname, rtype))
    elif ok:
        msg.reply("{} is added to resouce type:{}".format(rname, rtype))
    else:
        msg.reply("Error: {} is not added to resouce type:{}".format(rname, rtype))


@respond_to('^\s*remove\s+(\w+)\s+(\w+)\s*$')
def remove_resource(msg, rtype, rname):
    ch = msg.channel._body['name']
    conn = db.get_conn()
    try:
        ok = True
        rtype_exist = True
        rname_exist = True

        if not is_exist_resouce_type(conn, ch, rtype):
            rtype_exist = False
            raise(IsNotExistException("resource type is not existed!"))

        if not is_exist_resouce(conn, ch, rtype, rname):
            rname_exist = False
            raise(IsNotExistException("resource is not existed!"))

        uid = get_resource_status(conn, ch, rtype, rname)
        if uid is not None:
            raise(IsLockedException("resource is locked!"))

        cur = conn.cursor()
        cur.execute("""
            DELETE FROM resources
            WHERE channel = ?
            AND type = ?
            AND name = ?
        """, (ch, rtype, rname))
        cur.close()
    except IsNotExistException:
        pass
    except IsLockedException:
        pass
    except Exception:
        conn.rollback()
        ok = False
    finally:
        conn.commit()
        conn.close()

    if not rtype_exist:
        msg.reply("resouce type:{} is not existed in this channel".format(rtype))
    elif not rname_exist:
        msg.reply("{} is not existed in resource type:{}".format(rname, rtype))
    elif uid is not None:
        msg.reply("Oops! {} is used by <@{}> in resource type:{}".format(rname, uid, rtype))
    elif ok:
        msg.reply("{} is removed from resource type:{}".format(rname, rtype))
    else:
        msg.reply("Error: {} is not removed from resource type:{}".format(rname, rtype))


@respond_to('^\s*lock\s+(\w+)\s+(\w+)\s*$')
def lock_resource(msg, rtype, rname):
    ch = msg.channel._body['name']
    uid = msg.channel._body['creator']
    conn = db.get_conn()
    try:
        ok = True
        rtype_exist = True
        rname_exist = True

        if not is_exist_resouce_type(conn, ch, rtype):
            rtype_exist = False
            raise(IsNotExistException("resource type is not existed!"))

        if not is_exist_resouce(conn, ch, rtype, rname):
            rname_exist = False
            raise(IsNotExistException("resource is not existed!"))

        lock_uid = get_resource_status(conn, ch, rtype, rname)
        if lock_uid is not None:
            raise(IsLockedException("resource is locked!"))

        cur = conn.cursor()
        cur.execute("""
            UPDATE resources
            SET user = ?
            WHERE channel = ?
            AND type = ?
            AND name = ?
        """, (uid, ch, rtype, rname))
        cur.close()
    except IsNotExistException:
        pass
    except IsLockedException:
        pass
    except Exception:
        conn.rollback()
        ok = False
    finally:
        conn.commit()
        conn.close()

    if not rtype_exist:
        msg.reply("resouce type:{} is not existed in this channel".format(rtype))
    elif not rname_exist:
        msg.reply("{} is not existed in resource type:{}".format(rname, rtype))
    elif lock_uid is not None:
        msg.reply("Oops! {} is used by <@{}> in resource type:{}".format(rname, lock_uid, rtype))
    elif ok:
        msg.reply("OK. You can use {} in resource type:{}".format(rname, rtype))
    else:
        msg.reply("Error: {} is not locked in resource type:{}".format(rname, rtype))


@respond_to('^\s*unlock\s+(\w+)\s+(\w+)\s*$')
def unlock_resource(msg, rtype, rname):
    ch = msg.channel._body['name']
    uid = msg.channel._body['creator']
    conn = db.get_conn()
    try:
        ok = True
        rtype_exist = True
        rname_exist = True

        if not is_exist_resouce_type(conn, ch, rtype):
            rtype_exist = False
            raise(IsNotExistException("resource type is not existed!"))

        if not is_exist_resouce(conn, ch, rtype, rname):
            rname_exist = False
            raise(IsNotExistException("resource is not existed!"))

        lock_uid = get_resource_status(conn, ch, rtype, rname)
        if lock_uid is None:
            raise(IsUnlockedException("resource is not locked!"))
        elif lock_uid != uid:
            raise(IsUnlockedException("lock and unlock user is not equal!"))

        cur = conn.cursor()
        cur.execute("""
            UPDATE resources
            SET user = NULL
            WHERE channel = ?
            AND type = ?
            AND name = ?
        """, (ch, rtype, rname))
        cur.close()
    except IsNotExistException:
        pass
    except IsUnlockedException:
        pass
    except Exception:
        conn.rollback()
        ok = False
    finally:
        conn.commit()
        conn.close()

    if not rtype_exist:
        msg.reply("resouce type:{} is not existed in this channel".format(rtype))
    elif not rname_exist:
        msg.reply("{} is not existed in resource type:{}".format(rname, rtype))
    elif lock_uid is None:
        msg.reply("Oops! {} is not used already in resource type:{}".format(rname, rtype))
    elif lock_uid != uid:
        msg.reply("Oops! {} is used by <@{}> in resource type:{}. You don't have permission.".format(rname, lock_uid, rtype))
    elif ok:
        msg.reply("OK. I'll release {} in resource type:{}".format(rname, rtype))
    else:
        msg.reply("Error: {} is not unlocked in resource type:{}".format(rname, rtype))


@respond_to('^\s*force_unlock\s+(\w+)\s+(\w+)\s*$')
def force_unlock_resource(msg, rtype, rname):
    ch = msg.channel._body['name']
    conn = db.get_conn()
    try:
        ok = True
        rtype_exist = True
        rname_exist = True

        if not is_exist_resouce_type(conn, ch, rtype):
            rtype_exist = False
            raise(IsNotExistException("resource type is not existed!"))

        if not is_exist_resouce(conn, ch, rtype, rname):
            rname_exist = False
            raise(IsNotExistException("resource is not existed!"))

        lock_uid = get_resource_status(conn, ch, rtype, rname)
        if lock_uid is None:
            raise(IsUnlockedException("resource is not locked!"))

        cur = conn.cursor()
        cur.execute("""
            UPDATE resources
            SET user = NULL
            WHERE channel = ?
            AND type = ?
            AND name = ?
        """, (ch, rtype, rname))
        cur.close()
    except IsNotExistException:
        pass
    except IsUnlockedException:
        pass
    except Exception:
        conn.rollback()
        ok = False
    finally:
        conn.commit()
        conn.close()

    if not rtype_exist:
        msg.reply("resouce type:{} is not existed in this channel".format(rtype))
    elif not rname_exist:
        msg.reply("{} is not existed in resource type:{}".format(rname, rtype))
    elif lock_uid is None:
        msg.reply("Oops! {} is not used already in resource type:{}".format(rname, rtype))
    elif ok:
        msg.reply("OK. I'll release {} in resource type:{} by force".format(rname, rtype))
    else:
        msg.reply("Error: {} is not unlocked in resource type:{}".format(rname, rtype))
