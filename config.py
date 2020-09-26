# -*- coding: utf8 -*-

"""Global configuration for simple Password Manager.
by Tobias Küster, 2018

This file contains some variables for global configuration, such as some
useful defaults etc.
"""

import os
from pwdmgr_model import Configuration

USER_DIR = os.environ["HOME"]
CONFIG_PATH = os.path.join(USER_DIR, ".config", "pwdmgr")
DATE_FORMAT = "%Y-%m-%d"

DEFAULT_CONFIG = Configuration("xxx.xxx@xxx.xxx", os.path.join(USER_DIR, "pwds.json.gpg"))

def load_config() -> Configuration:
	# check file in home dir, try to load config
	# all okay -> return config
	# file does not exist -> create config
	# file exists, but unknown format -> error
	return DEFAULT_CONFIG
	
def create_config() -> Configuration:
	# ask user for e-mail address and password file
	# for now, just use input(), later extend with simple UI
	pass




