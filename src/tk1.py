#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""User interface for simple Password Manager.
by Tobias Küster, 2022

Another try with Tkinter for a more portable UI. Less focus on one huge table,
instead tags list, simple table, and edit dialogue, a bit like KeePass...
"""

import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog
import tkinter.messagebox

import pwdmgr_core
import pwdmgr_model
import config



ATTRIBUTES = {
	"label": "Label",
	"username": "Username",
	"password": "Password",
	"email": "E-Mail",
	"url": "URL",
	"notes": "Notes",
	"tags": "Tags",
	"last_changed": "Last Changed",
}


class PwdMgrFrame(tkinter.Frame):
	
	def __init__(self, root):
		super().__init__(root)
		root.title("Password Manager")
		
		self.config = pwdmgr_model.Configuration("test@test.com", "test.json")
		self.passwords = pwdmgr_model.create_test_passwords(10)
		self.grid()
		
		# Buttons: Add/Remove
		tkinter.Button(self, text="Add", command=self.add_password).grid(row=0, column=1, sticky="EW")
		tkinter.Button(self, text="edit", command=self.edit_password).grid(row=0, column=2, sticky="EW")
		tkinter.Button(self, text="Remove", command=self.remove_password).grid(row=0, column=3, sticky="EW")

		tags = list(set(t.strip() for p in self.passwords for t in p.tags.split(",")))
		var = tk.Variable(value=tags)
		self.listbox = tk.Listbox(
			self,
			listvariable=var,
			height=6,
			selectmode=tk.EXTENDED
		)
		self.listbox.bind('<<ListboxSelect>>', self.list_items_selected)
		self.listbox.grid(row=1, column=0, sticky="nsew")

		# define columns
		columns = ("label", "url", "tags", "last_changed")
		self.tree = ttk.Treeview(self, columns=columns, show='headings')
		for col in columns:
			self.tree.heading(col, text=ATTRIBUTES[col])

		# add data to the treeview
		for pwd in self.passwords:
			self.tree.insert('', tk.END, values=[pwd.label, pwd.url, pwd.tags, pwd.last_changed])

		self.tree.grid(row=1, column=1, sticky='nsew', columnspan=3)

	def get_selected(self):
		iid = self.tree.focus()
		idx = self.tree.index(iid)
		print(iid, idx)
		return self.passwords[idx]

	def list_items_selected(self, event):
		selected_indices = self.listbox.curselection()
		selected_langs = ",".join([self.listbox.get(i) for i in selected_indices])
		print(f'You selected: {selected_langs}')

		
	def add_password(self):
		print("adding...")
		# TODO create new password, open edit dialogue
		# if okay clicked, add password to list

	def edit_password(self):
		pwd = self.get_selected()
		dialog = EditPwdWindow(self, pwd)
		self.wait_window(dialog)
		print(dialog.password)

	def remove_password(self):
		for selected_item in self.tree.selection():
			pass
			# TODO not really delete the password, but set state to deleted
			self.tree.delete(selected_item)


class EditPwdWindow(tk.Toplevel):
	
	def __init__(self, parent, password):
		super().__init__(parent)

		self.password = password
		variables = {k: tk.StringVar() for k in ATTRIBUTES}

		for att, var in variables.items():
			row = tk.Frame(self)
			row.pack(side="top", fill="x", padx=5, pady=5)

			var.set(getattr(self.password, att))
			
			tk.Label(row, text=ATTRIBUTES[att]).pack(side="left")
			tk.Entry(row, textvariable=var).pack(side="right", fill="x")
		
		def do_cancel():
			print("cancel")
			self.destroy()
			
		def do_okay():
			print("okay")
			values = {att: var.get() for att, var in variables.items()}
			self.password = pwdmgr_model.Password(**values)
			self.destroy()
		
		row = tk.Frame(self)
		row.pack(side="top", fill="x")
		okay = tk.Button(row, text="Okay", command=do_okay).pack(side="right")
		cancel = tk.Button(row, text="Cancel", command=do_cancel).pack(side="right")
		


if __name__ == "__main__":

	root = tkinter.Tk()
	frame = PwdMgrFrame(root)
	root.mainloop()
