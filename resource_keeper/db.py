# -*- coding: utf-8 -*-

import os
import sqlite3
import toml


dir_path = os.path.abspath(os.path.dirname(__file__))
with open("{}/conf.toml".format(dir_path), "rt") as f:
    conf = toml.load(f)


def get_conn():
    conn = sqlite3.connect(conf['path']['db'])
    return conn
