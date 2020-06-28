#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""User interface for simple Password Manager.
by Tobias Küster, 2020

Third try of password manager UI, this time using GTK (first time using it).
Should hopefully provide a better UX than Tkinter.

- automatically decrypts on loading and encrypts on saving
- shows passwords in a list and with details
- provides edit fields for all attributes
- provides basic search/filter feature

TODO
- show warning when trying to close without saving changes
- test whether saving changes worked, e.g. by checking file change date
- actions for copy to clipboard, open URL, and similar
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import pwdmgr_core, pwdmgr_model, config
import os


class PwdMgrFrame(Gtk.Window):
	
	def __init__(self, conf, filename):
		super().__init__(title="Password Manager")
		self.conf = conf
		self.filename = filename
		self.resize(600, 400)
		
		# TODO use proper Gtk.SearchBar for filtering
		
		# ~self.grid()
		# ~self.next_filter = None

		# ~self.fltr = tkinter.StringVar()
		# ~self.fltr.trace("w", self.schedule_filter)
		
		# ~tkinter.Entry(self, textvariable=self.fltr).grid(row=0, column=0, sticky="EW")
		# ~tkinter.Button(self, text="<<", command=self.clear_fltr).grid(row=0, column=1, sticky="EW")	
		# ~tkinter.Button(self, text="+", command=self.add_password).grid(row=0, column=2, sticky="EW")
		# ~tkinter.Button(self, text="-", command=self.remove_password).grid(row=0, column=3, sticky="EW")
		# ~tkinter.Button(self, text="w!", command=self.save).grid(row=0, column=4, sticky="EW")

		# ~self.button = Gtk.Button(label="Click Here")
		# ~self.button.connect("clicked", self.on_button_clicked)
		# ~self.add(self.button)

		scroller = Gtk.ScrolledWindow()
		self.add(scroller)

		self.table = PwdTable()
		self.table.show_passwords(self.conf.passwords)
		scroller.add(self.table)

		# ~# frame within canvas with scroll bars... why does this have to be so hard?
		# ~canvas = tkinter.Canvas(self, width=1000, height=500)

		# ~self.table = PwdTable(canvas)
		# ~self.table.show_passwords(self.conf.passwords)
		# ~self.table.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

		# ~vbar = tkinter.Scrollbar(self, orient="vertical", command=canvas.yview)
		# ~hbar = tkinter.Scrollbar(self, orient="horizontal", command=canvas.xview)
		# ~canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)

		# ~vbar.grid(row=1, column=6, sticky="ns")
		# ~hbar.grid(row=2, column=0, columnspan=5, sticky="ew")
		
		# ~canvas.grid(row=1, column=0, columnspan=5, sticky="nswe")
		# ~canvas.create_window((4,4), window=self.table, anchor="nw")


	def clear_fltr(self):
		print("clearing filter")
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
			print("removing passwords")
			for entry in self.filter_list():
				self.conf.passwords.remove(entry)
			self.clear_fltr()


class PwdTable(Gtk.TreeView):
	
	def __init__(self):
		self.store = Gtk.ListStore(str, str, str, str, str, str, str, str)
		super().__init__(model=self.store)
		self.set_headers_clickable(True)
		
		for i, att in enumerate(pwdmgr_model.ATTRIBUTES):
			renderer = Gtk.CellRendererText(mode=Gtk.CellRendererMode.EDITABLE)
			print(dir(renderer))

			def edited(widget, path, text, i=i):
				print("path", path)
				print(self.store[path])
				print(self.store[path][1])
				self.store[path][i] = text
			
			renderer.set_property("editable", True)
			renderer.connect("edited", edited)
			
			column = Gtk.TreeViewColumn(att, renderer, text=i)
			column.set_sort_column_id(i)
			self.append_column(column)
		
	def show_passwords(self, passwords):
		# remove old children from grid
		
		self.store.clear()
		
		for entry in passwords:
			vals = [getattr(entry, att) for att in pwdmgr_model.ATTRIBUTES]
			print(vals)
			self.store.append(vals)
		

if __name__ == "__main__":
	try:
		filename = config.DEFAULT_PASSWORDS_FILE
		conf = pwdmgr_core.load_decrypt(filename)
	except IOError:
		filename="test.json"
		conf = pwdmgr_model.create_test_config()
	
	frame = PwdMgrFrame(conf, filename)
	frame.connect("destroy", Gtk.main_quit)
	frame.show_all()
	Gtk.main()
