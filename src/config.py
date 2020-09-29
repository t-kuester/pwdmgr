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
CONFIG_PATH = os.path.join(USER_DIR, ".config", "t-kuester")
CONFIG_FILE = os.path.join(CONFIG_PATH, "pwdmgr")

def load_config() -> Configuration:
	"""Try to load configuration file or create new file. May fail if a file
	with that name exists, but can not be read.
	"""
	try:
		with open(CONFIG_FILE, "r") as f:
			return Configuration(**json.load(f))
	except FileNotFoundError:
		config = create_config()
		os.makedirs(CONFIG_PATH)
		with open(CONFIG_FILE, "w") as f:
			json.dump(dict(config.__dict__), f, indent=4)
		return config
	
def create_config() -> Configuration:
	"""Ask user for new configuration detail, esp. e-mail and password path.
	"""
	print(f"Creating new Configuration at {CONFIG_FILE}...")
	mail = input("Enter e-mail identity to be used for encryption: ")
	path = input("Enter path to passwords file: ")
	return Configuration(mail, path)
