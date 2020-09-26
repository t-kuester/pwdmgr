# -*- coding: utf8 -*-

"""Global configuration for simple Password Manager.
by Tobias Küster, 2018

This file contains some variables for global configuration, such as some
useful defaults etc.
"""

import os
import json
from pwdmgr_model import Configuration

USER_DIR = os.environ["HOME"]
CONFIG_PATH = os.path.join(USER_DIR, ".config", "pwdmgr")
DATE_FORMAT = "%Y-%m-%d"

def load_config() -> Configuration:
	# check file in home dir, try to load config
	# all okay -> return config
	# file does not exist -> create config
	# file exists, but unknown format -> error
	try:
		with open(CONFIG_PATH, "r") as f:
			return Configuration(**json.load(f))
	except FileNotFoundError:
		config = create_config()
		print(config)
		with open(CONFIG_PATH, "w") as f:
			json.dump(dict(config.__dict__), f)
		return config
	except:
		print(f"Could not read config file at {CONFIG_PATH}")
		exit(1)
	
def create_config() -> Configuration:
	# ask user for e-mail address and password file
	# for now, just use input(), later extend with simple UI
	print(f"Creating new Configuration at {CONFIG_PATH}...")
	mail = input("Enter e-mail identity to be used for encryption: ")
	path = input("Enter path to passwords file: ")
	return Configuration(mail, path)
