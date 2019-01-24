#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""A Simple command-line tool for generating random passwords.
by Tobias Küster, 2019

optional arguments:
  -n, --num NUM  Number of characters
  -l, --lower    Allow lowercase characters?
  -u, --upper    Allow uppercase characters?
  -d, --digit    Allow digit characters?
  -p, --punct    Allow punctuation characters?
"""

import random, string, argparse

def generate(num=20, lower=True, upper=True, digit=True, punct=True):
	""" Generate a random password of given length with given character
	groups.	Even if character group is selected, password is not guaranteed
	to have one or more of each group.
	"""
	groups = [g for b, g in ((lower, string.ascii_lowercase),
	                         (upper, string.ascii_uppercase),
	                         (digit, string.digits),
	                         (punct, string.punctuation)) if b]
	return ''.join(random.choice(random.choice(groups)) for _ in range(num))

def main():
	""" for use from command line
	"""
	parser = argparse.ArgumentParser(description = "Simple Password Generator")
	parser.add_argument("-n, --num", type=int, default=10, dest="num", help="Number of characters")
	parser.add_argument("-l, --lower", action='store_true', dest="lower", help="Allow lowercase characters?")
	parser.add_argument("-u, --upper", action='store_true', dest="upper", help="Allow uppercase characters?")
	parser.add_argument("-d, --digit", action='store_true', dest="digit", help="Allow digit characters?")
	parser.add_argument("-p, --punct", action='store_true', dest="punct", help="Allow punctuation characters?")
	args = parser.parse_args()

	print(generate(args.num, args.lower, args.upper, args.digit, args.punct))
	
if __name__ == "__main__":
	main()
