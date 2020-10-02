#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Core Components for simple Password Manager.
by Tobias Küster, 2018

This module handles loading, saving, and most importantly, encrypting and
decrypting the password files.
"""

from config import *
from pwdmgr_model import load_from_json, write_to_json, Configuration, Password
from typing import List
import os, shutil
import gnupg


def load_decrypt(config: Configuration) -> List[Password]:
	"""Load and decrypt passwords from given file.
	"""
	print("decrypting...")
	gpg = gnupg.GPG(gnupghome=USER_DIR + "/.gnupg")
	with open(config.filename, "rb") as f:
		crypt = gpg.decrypt_file(f)
		if crypt.ok:
			return load_from_json(str(crypt))
		else:
			raise Exception(crypt.status)
	
def save_encrypt(config: Configuration, passwords: List[Password]):
	"""Encrypt and save passwords to given file.
	"""
	print("ecrypting...")
	gpg = gnupg.GPG(gnupghome=USER_DIR + "/.gnupg")
	
	if os.path.isfile(config.filename):
		shutil.copy(config.filename, config.filename + ".bak")
	with open(config.filename, "w") as f:
		s = write_to_json(passwords)
		crypt = gpg.encrypt(s, config.usermail)
		if crypt.ok:
			f.write(str(crypt))
		else:
			raise Exception(crypt.status)

def test():
	"""Just for testing loading, saving, encrytion and decryption.
	"""
	from pwdmgr_model import create_test_config, create_test_passwords
	conf = create_test_config()
	pwds = create_test_passwords()
	save_encrypt(conf, pwds)
	pwds2 = load_decrypt(conf)
	print(pwds2)
	assert pwds == pwds2

# testing stuff	
if __name__ == "__main__":
	test()
