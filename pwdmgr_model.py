#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Data model for simple Passwort Manager.
by Tobias Küster, 2018

Data model for stored passwords, with attributes such as a label, username and
password, tags, date of last change, etc.
"""

# from config import *
import json

ATTRIBUTES = "label", "username", "password", "notes", "tags", "last_changed"

class Password:
	"""Class representing a single password.
	"""

	def __init__(self, label, username, password, notes, tags, last_changed):
		self.label = label
		self.username = username
		self.password = password
		self.notes = notes
		self.tags = tags
		self.last_changed = last_changed

	def __repr__(self):
		return "Password(%r, %r, %r, %r, %r, %r)" % (self.label, self.username,
				self.password, self.notes, self.tags, self.last_changed)

class Configuration:
	"""Configuration for the password manager. Currently, this only wraps a list
	of passwords, but might be extended with more preferences (or removed).
	"""

	def __init__(self, passwords=None):
		self.passwords = passwords or []

	def __repr__(self):
		return "Configuration(%r)" % (self.passwords)


def load_from_json(json_str):
	"""Load password configuration from JSON string.
	"""
	config = json.loads(json_str)
	config["passwords"] = [Password(**d) for d in config["passwords"]]
	return Configuration(**config)
	
def write_to_json(configuration):
	"""Store password configuration in JSON string.
	"""
	config = dict(configuration.__dict__)
	config["passwords"] = [d.__dict__ for d in config["passwords"]]
	return json.dumps(config, sort_keys=True, indent=4, separators=(',', ': '))

# TODO load/save using CSV for more compact files?

def create_test_config():
	"""Create dummy config for testing.
	"""
	return Configuration([Password("label1", "name1", "pwd1", "url1", "tag1, tag2", "changed1"),
	                      Password("label2", "name2", "pwd2", "url2", "tag2, tag3", "changed2"),
			              Password("label3", "name3", "pwd3", "url3", "tag3, tag4", "changed3")])

def test():
	"""Just for testing basic creation and JSON serialization.
	"""
	conf = create_test_config()
	s = write_to_json(conf)
	conf2 = load_from_json(s)
	print(s)
	print(conf)
	print(conf2)
	assert str(conf) == str(conf2)

# testing stuff
if __name__ == "__main__":
	test()
