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
	
	def __init__(self, root, conf):
		super().__init__(root)
		self.config = conf
		
		self.grid()
		
		# TODO
		# password combo (later: list)
		# details area
		# button: save
		# button: copy
		# button: open
		# button: changed now
		# search/filter
		# button: generate
		
		# Buttons: Add/Remove
		tkinter.Button(self, text="Add", command=self.add_password).grid(row=1, column=0, sticky="EW")
		tkinter.Button(self, text="Remove", command=self.remove_password).grid(row=1, column=1, sticky="EW")
		
		# Optionmenu with passwords in the config
		self.selected = tkinter.StringVar()
		self.selected.trace("w", self.update_selected)
		self.passwords = tkinter.OptionMenu(self, self.selected, *(p.label for p in self.config.passwords))
		self.passwords.grid(row=2, column=0, columnspan=2, sticky="EW")
		
		# PasswordPanel showing the selected password
		self.panel = PasswordPanel(self)
		self.panel.grid(row=3, column=0, columnspan=2, sticky="EW")
		
		# TODO add tracer to dirty boolean var to enable/disable save button
		
		# TODO add buttons


	def get_selected(self):
		label = self.selected.get()
		return next((p for p in self.config.passwords if p.label == label), None)

	def update_options(self):
		# ugly hack: https://stackoverflow.com/a/19795103/1639625
		menu = self.passwords.children["menu"]
		menu.delete(0, "end")
		for l in (p.label for p in self.config.passwords):
			menu.add_command(label=l, command=lambda v=l: self.selected.set(v))

	def update_selected(self, *args):
		self.panel.set_password(self.get_selected())

	def add_password(self):
		p = pwdmgr_model.Password("", "", "", "", "", "")
		self.config.passwords.append(p)
		self.update_options()
		self.selected.set(p.label)
		
	def remove_password(self):
		p = self.get_selected()
		if p:
			self.config.passwords.remove(p)
			self.update_options()
			self.selected.set(next((p.label for p in self.config.passwords), None))


class PasswordPanel(tkinter.Canvas):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.label  = tkinter.StringVar()
		self.name   = tkinter.StringVar()
		self.pwd    = tkinter.StringVar()
		self.url    = tkinter.StringVar()
		self.change = tkinter.StringVar()
		self.tags   = tkinter.StringVar()

		labels = "Label", "Username", "Password", "URL", "Last Change", "Tags"
		varbls = self.label, self.name, self.pwd, self.url, self.change, self.tags
		for r, (l, v) in enumerate(zip(labels, varbls)):
			tkinter.Label(self, text=l).grid(row=r, column=0, sticky="NW")
			tkinter.Entry(self, textvariable=v).grid(row=r, column=1, sticky="W")
			v.trace("w", self.set_dirty)

		self.set_password(None)

	def set_dirty(self, *args):
		self.dirty = True
	
	def set_password(self, pwd):
		self.password = pwd
		self.dirty = False
		self.label.set(pwd.label if pwd else "") 
		self.name.set(pwd.username if pwd else "")
		self.pwd.set(pwd.password if pwd else "")
		self.url.set(pwd.url if pwd else "")
		self.change.set(pwd.last_changed if pwd else "")
		self.tags.set(pwd.tags if pwd else "")

	def update_password(self):
		self.password.label = self.label.get()
		self.password.username = self.name.get()
		self.password.password = self.pwd.get()
		self.password.url = self.url.get()
		self.password.last_changed = self.change.get()
		self.password.tags = self.tags.get()


if __name__ == "__main__":
	filename = config.DEFAULT_PASSWORDS_FILE
	try:
		conf = pwdmgr_core.load_decrypt(filename)
	except IOError:
		conf = pwdmgr_model.create_test_config()

	root = tkinter.Tk()
	frame = PwdMgrFrame(root, conf)
	root.title("Password Manager")
	root.mainloop()

	pwdmgr_core.save_encrypt(filename, conf)
