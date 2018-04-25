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
import os


def load_decrypt(filename, passphrase=None):
	"""Load and decrypt passwords from given file.
	"""
	print("decrypting")
	p = os.popen('gpg --decrypt "%s.gpg"' % filename)
	s = p.read()
	# TODO send passphrase to input
	return pwdmgr_model.load_from_json(s)

	
def save_encrypt(filename, config):
	"""Encrypt and save passwords to given file.
	"""
	print("ecrypting")
	s = pwdmgr_model.write_to_json(config)
	os.system('echo \'%s\' | gpg --recipient "%s" --output "%s.gpg" --yes --encrypt' % (s, DEFAULT_USER, filename))


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
