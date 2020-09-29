#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Data model for simple Passwort Manager.
by Tobias Küster, 2018

Data model for stored passwords, with attributes such as a label, username and
password, tags, date of last change, etc.
"""

# from config import *
from typing import List
import json

ATTRIBUTES = "label", "username", "password", "email", "url", "notes", "tags", "last_changed"

class Password:
	"""Class representing a single password.
	"""

	def __init__(self, label, username, password, email, url, notes, tags, last_changed):
		self.label = label
		self.username = username
		self.password = password
		self.email = email
		self.url = url
		self.notes = notes
		self.tags = tags
		self.last_changed = last_changed

	def values(self):
		return [getattr(self, att) for att in ATTRIBUTES]

	def __eq__(self, other):
		return isinstance(other, Password) and self.values() == other.values()

	def __repr__(self):
		return "Password(%r, %r, %r, %r, %r, %r, %r, %r)" % (self.label, self.username,
				self.password, self.email, self.url, self.notes, self.tags, self.last_changed)


class Configuration:
	"""Configuration for the password manager.
	"""

	def __init__(self, usermail, filename):
		self.usermail = usermail
		self.filename = filename

	def __repr__(self):
		return "Configuration(%r, %r)" % (self.usermail, self.filename)


def load_from_json(json_str: str) -> List[Password]:
	"""Load password configuration from JSON string.
	"""
	return [Password(**d) for d in json.loads(json_str)]
	
def write_to_json(passwords: List[Password]) -> str:
	"""Store password configuration in JSON string.
	"""
	return json.dumps([p.__dict__ for p in passwords],
	                  sort_keys=True, indent=4, separators=(',', ': '))


def create_test_passwords(n: int = 5) -> List[Password]:
	"""Create dummy passwords for testing.
	"""
	return [Password(**{a: f"{a}{i}" for a in ATTRIBUTES}) for i in range(n)]

def create_test_config() -> Configuration:
	"""Create dummy config for testing.
	"""
	return Configuration(input("Enter Mail for testing: "), "test.json")

def test():
	"""Just for testing basic creation and JSON serialization.
	"""
	pwds = create_test_passwords()
	s = write_to_json(pwds)
	pwds2 = load_from_json(s)
	print(s)
	print(pwds)
	print(pwds2)
	assert pwds == pwds2

# testing stuff
if __name__ == "__main__":
	test()
