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

- highlight changed entries
TODO
- highlight deleted entries
- show warning when trying to close without saving changes
- create backup of original file
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
		self.dirty = False
		self.connect("destroy", self.close)

		self.search = Gtk.SearchEntry()
		self.search.connect("search-changed", self.do_filter)

		self.status = Gtk.Label()
		
		button_add = Gtk.Button(label="+")
		button_add.connect("clicked", self.add_password)
		
		button_del = Gtk.Button(label="-")
		button_del.connect("clicked", self.remove_password)

		self.table = self.make_table(self.conf.passwords)
		scroller = Gtk.ScrolledWindow()
		scroller.add(self.table)
		
		header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		header.pack_start(Gtk.Label(label="Filter"), False, False, 10)
		header.pack_start(self.search, False, False, 0)
		header.pack_start(self.status, False, False, 0)
		header.pack_end(button_del, False, False, 0)
		header.pack_end(button_add, False, False, 0)
		body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		body.pack_start(header, False, False, 0)
		body.pack_start(scroller, True, True, 0)
		self.add(body)

	def do_filter(self, *args):
		print("FILTER", args)

	def close(self, frame):
		# TODO check whether dirty
		if self.dirty:
			print("DIRTY")
		Gtk.main_quit(frame)

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

	def make_table(self, passwords):
		self.store = Gtk.ListStore(str, str, str, str, str, str, str, str, str)
		table = Gtk.TreeView(model=self.store)
		table.set_headers_clickable(True)
		
		for i, att in enumerate(pwdmgr_model.ATTRIBUTES):
			renderer = Gtk.CellRendererText()

			def edited(widget, path, text, i=i, r=renderer):
				values = self.store[path]
				pwd = self.find(passwords, values)
				print()
				print(pwd)
				
				if self.store[path][i] != text:
					self.store[path][i] = text
					pwd[i] = text
					self.store[path][8] = "#eeee88"
					print(*passwords, sep="\n")
					self.dirty = True
			
			renderer.set_property("editable", True)
			renderer.connect("edited", edited)
			
			column = Gtk.TreeViewColumn(att, renderer, text=i, background=8)
			column.set_sort_column_id(i)
			table.append_column(column)
		
		for entry in passwords:
			vals = [getattr(entry, att) for att in pwdmgr_model.ATTRIBUTES]
			print(vals)
			vals += ["white"]
			self.store.append(vals)
		return table
	
	def find(self, passwords, values):
		return next(p for p in passwords if all(a==b for a, b in zip(p, values)))
		

if __name__ == "__main__":
	# ~try:
		# ~filename = config.DEFAULT_PASSWORDS_FILE
		# ~conf = pwdmgr_core.load_decrypt(filename)
	# ~except IOError:
	filename="test.json"
	conf = pwdmgr_model.create_test_config()
	
	frame = PwdMgrFrame(conf, filename)
	frame.show_all()
	Gtk.main()
