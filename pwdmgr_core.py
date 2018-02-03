#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Core Components for simple Password Manager.
by Tobias Küster, 2018

This module handles loading, saving, and most importantly, encrypting and
decrypting the password files.

For the first version, I'll just call the command line tools; later I'll
probably switch to some crypto library, but haven't decided which, yet.

In the VERY first iteration this is not doing any encryption at all, just for
testing, so don't use this for your real passwords yet!
"""

from config import *
import pwdmgr_model


def load_decrypt(filename):
	"""Load and decrypt passwords from given file.
	"""
	with open(filename, "r") as f:
		s = f.read()
		return pwdmgr_model.load_from_json(s)
	
def save_encrypt(filename, config):
	"""Encrypt and save passwords to given file.
	"""
	with open(filename, "w") as f:
		s = pwdmgr_model.write_to_json(config)
		f.write(s)


def test():
	"""Just for testing loading, saving, encrytion and decryption.
	"""
	filename = DEFAULT_PASSWORDS_FILE
	conf = pwdmgr_model.create_test_config()
	save_encrypt(filename, conf)
	conf2 = load_decrypt(filename)
	print(conf2)
	print(repr(conf) == repr(conf2))

# testing stuff	
if __name__ == "__main__":
	test()
