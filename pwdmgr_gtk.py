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
- highlight deleted entries
- show warning when trying to close without saving changes
TODO
- create backup of original file
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import pwdmgr_core, pwdmgr_model, config
import os

COLOR_NON = "#ffffff"
COLOR_NEW = "#aaffaa"
COLOR_DEL = "#ffaaaa"
COLOR_MOD = "#aaaaff"

class PwdMgrFrame:
	
	def __init__(self, conf, filename):
		self.conf = conf
		self.filename = filename
		self.dirty = False
		
		self.search = Gtk.SearchEntry()
		self.search.connect("search-changed", self.do_filter)
		
		header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		header.pack_start(Gtk.Label(label="Filter"), False, False, 10)
		header.pack_start(self.search, False, False, 0)
		header.pack_end(self.create_button("list-remove", self.do_remove), False, False, 0)
		header.pack_end(self.create_button("list-add", self.do_add), False, False, 0)
		
		body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		body.pack_start(header, False, False, 0)
		body.pack_start(self.create_table(), True, True, 0)
		
		self.window = Gtk.ApplicationWindow(title="Password Manager")
		self.window.resize(600, 400)
		self.window.connect("delete-event", self.do_close)
		self.window.connect("destroy", Gtk.main_quit)
		self.window.add(body)
		self.window.show_all()
		
	def create_button(self, icon, command):
		button = Gtk.Button.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
		button.connect("clicked", command)
		button.set_property("relief", Gtk.ReliefStyle.NONE)
		return button

	def do_filter(self, widget):
		print("filtering...", widget.get_text())
		self.list_filter.refilter()

	def do_close(self, *args):
		if self.dirty:
			if self.ask_dialog("Save Changes?", "Select 'No' to review changes"):
				print("saving...")
				pwdmgr_core.save_encrypt(self.filename, self.conf)
				return False
			else:
				return not self.ask_dialog("Exit Anyway?")
		return False

	def do_add(self, widget):
		if self.ask_dialog("Add Password"):
			print("adding password")
			p = pwdmgr_model.Password(*pwdmgr_model.ATTRIBUTES)
			self.conf.passwords.append(p)
			vals = [getattr(p, att) for att in pwdmgr_model.ATTRIBUTES] + [COLOR_NEW]
			self.store.append(vals)
			self.dirty = True
	
	def do_remove(self, widget):
		model, treeiter = self.select.get_selected()
		if treeiter is not None and \
				self.ask_dialog("Delete Selected?", "Mark selected passwort for deletion?"):
			print("removing passwords")
			self.list_filter[treeiter][8] = COLOR_DEL
			self.dirty = True
	
	def ask_dialog(self, title, message=None):
		dialog = Gtk.MessageDialog(parent=self.window, flags=0, 
			message_type=Gtk.MessageType.QUESTION, 
			buttons=Gtk.ButtonsType.YES_NO, text=title)
		dialog.format_secondary_text(message)
		res = dialog.run() == Gtk.ResponseType.YES
		dialog.destroy()
		return res
		
	def filter_func(self, model, iter, data):
		s = self.search.get_text().lower()
		return any(s in att.lower() for att in model[iter])
		
	def create_edit_func(self, column):
		def edited(widget, path, text):
			values = self.list_filter[path]
			pwd = self.match_entry(values)
			if self.list_filter[path][column] != text:
				self.list_filter[path][column] = text
				pwd[column] = text
				if self.list_filter[path][8] == COLOR_NON:
					self.list_filter[path][8] = COLOR_MOD
				self.dirty = True
		return edited
	
	def create_table(self):
		# create list model and populate with passwords
		self.store = Gtk.ListStore(*[str]*9)
		for entry in self.conf.passwords:
			vals = [getattr(entry, att) for att in pwdmgr_model.ATTRIBUTES] + [COLOR_NON]
			self.store.append(vals)
		
		# create filter on list model
		self.list_filter = self.store.filter_new()
		self.list_filter.set_visible_func(self.filter_func)
		
		# create Tree View with appropriate columns, editable and sortable
		table = Gtk.TreeView.new_with_model(self.list_filter)
		self.select = table.get_selection()
		
		for i, att in enumerate(pwdmgr_model.ATTRIBUTES):
			renderer = Gtk.CellRendererText()

			
			renderer.set_property("editable", True)
			renderer.connect("edited", self.create_edit_func(i))
			
			column = Gtk.TreeViewColumn(att, renderer, text=i, background=8)
			# ~column.set_sort_column_id(i)
			table.append_column(column)
		
		scroller = Gtk.ScrolledWindow()
		scroller.add(table)
		return scroller
	
	def match_entry(self, values):
		return next(p for p in self.conf.passwords if all(a==b for a, b in zip(p, values)))
		

if __name__ == "__main__":
	# ~try:
		# ~filename = config.DEFAULT_PASSWORDS_FILE
		# ~conf = pwdmgr_core.load_decrypt(filename)
	# ~except IOError:
	filename="test.json"
	conf = pwdmgr_model.create_test_config()
	
	PwdMgrFrame(conf, filename)
	Gtk.main()
