# -*- coding: utf8 -*-

"""Global configuration for simple Password Manager.
by Tobias Küster, 2018

This file contains some variables for global configuration, such as some
useful defaults etc.
"""

import os

USER_DIR = os.environ["HOME"]

DEFAULT_PASSWORDS_FILE = os.path.join(USER_DIR, "pwds.json")

DATE_FORMAT = "%Y-%m-%d"
