# -*- coding: utf-8 -*-

import os
import toml

dir_path = os.path.abspath(os.path.dirname(__file__))
with open("{}/conf.toml".format(dir_path), "rt") as f:
    conf = toml.load(f)

API_TOKEN = conf['slackbot']['api_token']
DEFAULT_REPLY = conf['slackbot']['default_reply']
PLUGINS = conf['slackbot']['plugins']
