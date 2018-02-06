#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""User interface for simple Password Manager.
by Tobias Küster, 2018

- automatically decrypts on loading and encrypts on saving
- shows passwords in a list and with details
- provides edit fields for all attributes
- provides basic search/filter feature
- actions for copy to clipboard, open URL, and similar
"""

import tkinter, tkinter.messagebox, tkinter.filedialog
import pwdmgr_core, pwdmgr_model, config
import os


class PwdMgrFrame(tkinter.Frame):
	
	def __init__(self, root, conf, filename):
		super().__init__(root)
		self.conf = conf
		self.filename = filename
		
		self.grid()

		fltr = tkinter.StringVar()
		fltr.trace("w", self.filter_list)
		
		tkinter.Entry(self, textvariable=fltr).grid(row=0, column=0, sticky="W")

		tkinter.Button(self, text="<<", command=self.clear_fltr).grid(row=0, column=1, sticky="EW")	
		tkinter.Button(self, text="+", command=self.add_password).grid(row=0, column=2, sticky="EW")
		tkinter.Button(self, text="-", command=self.remove_password).grid(row=0, column=3, sticky="EW")
		tkinter.Button(self, text="w!", command=self.save).grid(row=0, column=4, sticky="EW")

		self.table = PwdTable(self)
		self.table.grid(row=1, column=0, columnspan=5)
		
		# TODO
		# buttons: add, remove, save list
		# buttons: copy, open, changed now, generate
		# search/filter
		
	def clear_fltr(self):
		pass
		
	def filter_list(self, *args):
		pass
		
	def save(self):
		pwdmgr_core.save_encrypt(self.filename, self.conf)

	def add_password(self):
		p = pwdmgr_model.Password("", "", "", "", "", "")
		self.conf.passwords.append(p)
		
	def remove_password(self):
		p = self.get_selected()
		if p:
			self.config.passwords.remove(p)
			self.update_options()
			self.selected.set(next((p.label for p in self.conf.passwords), None))


class PwdTable(tkinter.Canvas):
	
	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent
		attributes = ("label", "username", "password", "url", "tags", "last_changed")
		
		self.grid()
		
		# widgets = []
		
		for col, attribute in enumerate(attributes):
			tkinter.Label(self, text=attribute).grid(row=0, column=col, sticky="NW")
		
		for row, pwd in enumerate(self.parent.conf.passwords, start=1):
			# d = {}
			for col, attribute in enumerate(attributes):
				var = tkinter.StringVar()
				var.set(getattr(pwd, attribute))
				tkinter.Entry(self, textvariable=var).grid(row=row, column=col, sticky="W")
				var.trace("w", lambda *args, v=var, a=attribute, p=pwd: setattr(p, a, v.get()))
				
				# d[attribute] = var
			# widgets.append(d)
	


if __name__ == "__main__":
	filename = config.DEFAULT_PASSWORDS_FILE
	try:
		conf = pwdmgr_core.load_decrypt(filename)
	except IOError:
		conf = pwdmgr_model.create_test_config()

	root = tkinter.Tk()
	frame = PwdMgrFrame(root, conf, filename)
	root.title("Password Manager")
	root.mainloop()
