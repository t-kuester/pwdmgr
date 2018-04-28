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
		self.next_filter = None

		self.fltr = tkinter.StringVar()
		self.fltr.trace("w", self.schedule_filter)
		
		tkinter.Entry(self, textvariable=self.fltr).grid(row=0, column=0, sticky="EW")
		tkinter.Button(self, text="<<", command=self.clear_fltr).grid(row=0, column=1, sticky="EW")	
		tkinter.Button(self, text="+", command=self.add_password).grid(row=0, column=2, sticky="EW")
		tkinter.Button(self, text="-", command=self.remove_password).grid(row=0, column=3, sticky="EW")
		tkinter.Button(self, text="w!", command=self.save).grid(row=0, column=4, sticky="EW")

		# frame within canvas with scroll bars... why does this have to be so hard?
		canvas = tkinter.Canvas(self, width=1000, height=500)

		self.table = PwdTable(canvas)
		self.table.show_passwords(self.conf.passwords)
		self.table.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

		vbar = tkinter.Scrollbar(self, orient="vertical", command=canvas.yview)
		canvas.configure(yscrollcommand=vbar.set)

		vbar.grid(row=1, column=6, sticky="ns")
		canvas.grid(row=1, column=0, columnspan=5, sticky="nswe")
		canvas.create_window((4,4), window=self.table, anchor="nw")


	def clear_fltr(self):
		print("clearing fitler")
		self.fltr.set("")

	def schedule_filter(self, *args):
		if self.next_filter:
			self.after_cancel(self.next_filter)
		self.next_filter = self.after(500, self.filter_list)

	def filter_list(self):
		print("filtering...")
		s = self.fltr.get().lower()
		filtered = [p for p in self.conf.passwords
		            if any(s in getattr(p, a).lower() for a in pwdmgr_model.ATTRIBUTES)]
		self.table.show_passwords(filtered)
		return filtered
		
	def save(self):
		if tkinter.messagebox.askokcancel("Save", "Save changes?"):
			print("saving...")
			pwdmgr_core.save_encrypt(self.filename, self.conf)

	def add_password(self):
		print("adding password")
		p = pwdmgr_model.Password("", "", "", "", "", "")
		self.conf.passwords.append(p)
		self.filter_list()
		
	def remove_password(self):
		if tkinter.messagebox.askokcancel("Remove", "Remove all shown entries?"):
			print("removing password")
			for entry in self.filter_list():
				self.conf.passwords.remove(entry)
			self.clear_fltr()


class PwdTable(tkinter.Frame):
	
	def __init__(self, parent, **kwargs):
		super().__init__(parent, **kwargs)
		
	def show_passwords(self, passwords):
		# remove old children from grid
		for child in self.grid_slaves():
			child.grid_forget()
		# add row with the attribute names
		if passwords:
			for col, attr in enumerate(pwdmgr_model.ATTRIBUTES):
				b = tkinter.Button(self, text=attr, relief="flat",
				                   command=self.sort_passwords(passwords, attr))
				b.grid(row=0, column=col, sticky="ew")
		# add rows with filtered passwords
		for row, pwd in enumerate(passwords, start=1):
			for col, attr in enumerate(pwdmgr_model.ATTRIBUTES):
				var = tkinter.StringVar()
				var.set(getattr(pwd, attr))
				tkinter.Entry(self, textvariable=var).grid(row=row, column=col, sticky="w")
				var.trace("w", lambda *args, v=var, a=attr, p=pwd: setattr(p, a, v.get()))

	def sort_passwords(self, passwords, attribute):
		def sort_inner():
			passwords.sort(key=lambda p: getattr(p, attribute))
			self.show_passwords(passwords)
		return sort_inner


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
