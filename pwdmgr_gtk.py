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

- highlight new/modified/deleted entries
- auto-save and encrypt when closing with changes (asking first)
- creating backup of original file

TODO
- scroll to newly created password
- EXCEPTION when filtered and removing the text that adds it to the filter
- toggle "show passwords"
- documentation
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

# indices for derived ID, color, and deleted status
N_ATT = len(pwdmgr_model.ATTRIBUTES)
IDX_ID, IDX_COL, IDX_DEL = N_ATT, N_ATT+1, N_ATT+2

class PwdMgrFrame:
	
	def __init__(self, conf, filename):
		self.conf = conf
		self.filename = filename
		
		self.create_model()
		
		self.search = Gtk.SearchEntry()
		self.search.connect("search-changed", self.do_filter)

		self.mod_only = Gtk.CheckButton(label="Modified Only")
		self.mod_only.set_active(False)
		self.mod_only.connect("toggled", self.do_filter)
		
		header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		header.pack_start(Gtk.Label(label="Filter"), False, False, 10)
		header.pack_start(self.search, False, False, 0)
		header.pack_start(self.mod_only, False, False, 10)
		header.pack_end(create_button("list-remove", self.do_remove), False, False, 0)
		header.pack_end(create_button("list-add", self.do_add), False, False, 0)
		
		body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		body.pack_start(header, False, False, 0)
		body.pack_start(self.create_table(), True, True, 0)
		
		self.window = Gtk.ApplicationWindow(title="Password Manager")
		self.window.resize(600, 400)
		self.window.connect("delete-event", self.do_close)
		self.window.connect("destroy", Gtk.main_quit)
		self.window.add(body)
		self.window.show_all()
		
	def do_filter(self, widget):
		print("filtering...", self.search.get_text(), self.mod_only.get_active())
		self.store_filter.refilter()

	def do_close(self, *args):
		new_passwords = [pwdmgr_model.Password(*vals[:N_ATT])
		                 for vals in self.store if not vals[IDX_DEL]]
		if new_passwords != self.conf.passwords:
			if ask_dialog(self.window, "Save Changes?", "Select 'No' to review changes"):
				print("saving...")
				self.conf.passwords = new_passwords
				pwdmgr_core.save_encrypt(self.filename, self.conf)
				return False
			else:
				return not ask_dialog(self.window, "Exit Anyway?")
		return False

	def do_add(self, widget):
		if ask_dialog(self.window, "Add Password"):
			print("adding password")
			vals = [*pwdmgr_model.ATTRIBUTES, -1, COLOR_NEW, False]
			self.store.append(vals)
	
	def do_remove(self, widget):
		model, it = self.select.get_selected()
		if it is not None and ask_dialog(self.window, "Delete Selected?", 
				"Mark/unmark selected passwort for deletion?"):
			print("setting delete mark")
			vals = model[it]
			vals[IDX_DEL] ^= True
			self.set_color(vals)
	
	def filter_func(self, model, it, data):
		vals = model[it]
		if self.mod_only.get_active() and vals[IDX_COL] == COLOR_NON:
			return False
		s = self.search.get_text().lower()
		return any(s in att.lower() for att in vals[:N_ATT])
		
	def create_edit_func(self, column):
		def edited(widget, path, text):
			values = self.store_filter[path]
			values[column] = text
			self.set_color(values)
		return edited
		
	def create_model(self):
		# create list model and populate with passwords
		# data format: Password attributes, then derived ID, Color, and Deleted?
		self.store = Gtk.ListStore(*[str]*8 + [int, str, bool])
		for i, entry in enumerate(self.conf.passwords):
			vals = [*entry.values(), i, COLOR_NON, False]
			self.store.append(vals)
		
		# create filter on list model
		self.store_filter = self.store.filter_new()
		self.store_filter.set_visible_func(self.filter_func)
	
	def create_table(self):
		# create Tree View with appropriate columns, editable and sortable
		table = Gtk.TreeView.new_with_model(self.store_filter)
		self.select = table.get_selection()
		
		renderer = Gtk.CellRendererText()
		table.append_column(Gtk.TreeViewColumn("id", renderer, text=IDX_ID, background=IDX_COL))
		
		for i, att in enumerate(pwdmgr_model.ATTRIBUTES):
			renderer = Gtk.CellRendererText()
			renderer.set_property("editable", True)
			renderer.connect("edited", self.create_edit_func(i))
			table.append_column(Gtk.TreeViewColumn(att, renderer, text=i, background=IDX_COL))
		
		scroller = Gtk.ScrolledWindow()
		scroller.add(table)
		return scroller
	
	def set_color(self, values):
		idx = values[IDX_ID]
		if values[IDX_DEL]:
			color = COLOR_DEL
		elif idx == -1:
			color = COLOR_NEW
		elif values[:N_ATT] != self.conf.passwords[idx].values():
			color = COLOR_MOD
		else:
			color = COLOR_NON
		values[IDX_COL] = color
		
		
def create_button(icon, command):
	button = Gtk.Button.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
	button.connect("clicked", command)
	button.set_property("relief", Gtk.ReliefStyle.NONE)
	return button

def ask_dialog(parent, title, message=None):
	dialog = Gtk.MessageDialog(parent=parent, flags=0, 
		message_type=Gtk.MessageType.QUESTION, 
		buttons=Gtk.ButtonsType.YES_NO, text=title)
	dialog.format_secondary_text(message)
	res = dialog.run() == Gtk.ResponseType.YES
	dialog.destroy()
	return res
	

if __name__ == "__main__":
	try:
		filename = config.DEFAULT_PASSWORDS_FILE
		conf = pwdmgr_core.load_decrypt(filename)
	except IOError:
		filename="test.json"
		conf = pwdmgr_model.create_test_config()
	
	PwdMgrFrame(conf, filename)
	Gtk.main()
