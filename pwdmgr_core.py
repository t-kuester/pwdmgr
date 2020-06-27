#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Core Components for simple Password Manager.
by Tobias Küster, 2018

This module handles loading, saving, and most importantly, encrypting and
decrypting the password files.
"""

from config import *
import pwdmgr_model
import os
import gnupg


def load_decrypt(filename, passphrase=None):
	"""Load and decrypt passwords from given file.
	"""
	print("decrypting...")
	gpg = gnupg.GPG(gnupghome=USER_DIR + "/.gnupg")
	with open(filename, "rb") as f:
		crypt = gpg.decrypt_file(f)
		if crypt.ok:
			return pwdmgr_model.load_from_json(str(crypt))
		else:
			raise Exception(crypt.status)
	
def save_encrypt(filename, config):
	"""Encrypt and save passwords to given file.
	"""
	print("ecrypting...")
	gpg = gnupg.GPG(gnupghome=USER_DIR + "/.gnupg")
	with open(filename, "w") as f:
		s = pwdmgr_model.write_to_json(config)
		crypt = gpg.encrypt(s, DEFAULT_USER)
		if crypt.ok:
			f.write(str(crypt))
		else:
			raise Exception(crypt.status)

def convert(oldfile):
	"""Read password file in my own old tabular format and convert to new form.
	"""
	import re
	pwds = []
	with open(oldfile) as f:
		for line in f:
			m = re.match("== (.+) ==", line)
			if m:
				tags = m.group(1).lower()
			elif line.strip():
				label, name, pwd, misc = map(str.strip, (line[:20], line[20:50], line[50:80], line[80:]))
				print(tags, label, name, pwd, misc)
				pwds.append(pwdmgr_model.Password(label, name, pwd, misc, tags, None))

	save_encrypt(DEFAULT_PASSWORDS_FILE, pwdmgr_model.Configuration(pwds))

def test():
	"""Just for testing loading, saving, encrytion and decryption.
	"""
	filename = "not-my-actual-pwds.json"
	conf = pwdmgr_model.create_test_config()
	save_encrypt(filename, conf)
	conf2 = load_decrypt(filename)
	print(conf2)
	print(repr(conf) == repr(conf2))

# testing stuff	
if __name__ == "__main__":
	test()
