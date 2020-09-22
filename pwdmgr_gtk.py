#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""User interface for simple Password Manager.
by Tobias Küster, 2020

Third try of password manager UI, this time using GTK (first time using it).
Should hopefully provide a better UX than Tkinter.

- automatically decrypts on loading and encrypts on saving (with backup)
- shows passwords and their attributes in a table
- provides basic search/filter feature
- highlight new/modified/deleted entries
- filter columns to be shown

TODO
- similar filter list with all tags
- EXCEPTION when editing a field that adds the row to the current filter
- add padding to botton for dumb GTK overlay-scrollbar?
- scroll to newly created password (seems to be not so easy...)
- try to enable sorting on top of filtering again
- Exception when filtered and removing the text that adds it to the filter
- toggle "show passwords"
- add "folders" in addition to tags/labels?
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import pwdmgr_core, pwdmgr_model, config
import os

# colors indicating the status of the Passwords
COLOR_NON = "#ffffff"
COLOR_NEW = "#aaffaa"
COLOR_DEL = "#ffaaaa"
COLOR_MOD = "#aaaaff"

# indices for derived ID, color, and deleted status
N_ATT = len(pwdmgr_model.ATTRIBUTES)
IDX_ID, IDX_COL, IDX_DEL = N_ATT, N_ATT+1, N_ATT+2

class PwdMgrFrame:
	""" Wrapper-Class for the GTK window and all its elements (but not in itself
	a subclass of Window), including callback methods for different actions.
	"""
	
	def __init__(self, conf, filename):
		""" Create Password Manager window for given config, filename for saving
		"""
		self.conf = conf
		self.filename = filename
		
		# create search and filtering windgets
		self.search = Gtk.SearchEntry()
		self.search.connect("search-changed", self.do_filter)
		self.mod_only = Gtk.CheckButton(label="Modified Only")
		self.mod_only.set_active(False)
		self.mod_only.connect("toggled", self.do_filter)

		# create tool bar and buttons
		header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
		header.pack_start(Gtk.Label(label="Filter"), False, False, 10)
		header.pack_start(self.search, False, False, 0)
		header.pack_start(self.mod_only, False, False, 10)
		header.pack_start(create_button("Select Columns", self.do_filter_columns, False), False, False, 0)
		header.pack_end(create_button("list-remove", self.do_remove), False, False, 0)
		header.pack_end(create_button("list-add", self.do_add), False, False, 0)
		
		# create table model and body section with table view
		self.create_model()
		self.table = self.create_table()
		self.column_menu = self.create_column_menu()
		table_scroller = Gtk.ScrolledWindow()
		table_scroller.add(self.table)
		
		body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		body.pack_start(header, False, False, 0)
		body.pack_start(table_scroller, True, True, 0)

		# put it all together in a window
		self.window = Gtk.ApplicationWindow(title="Password Manager")
		self.window.resize(800, 600)
		self.window.connect("delete-event", self.do_close)
		self.window.connect("destroy", Gtk.main_quit)
		self.window.add(body)
		self.window.show_all()
		
	def do_filter_columns(self, widget):
		""" Callback for showing the column-filter-menu; not the actual buttons
		"""
		self.column_menu.set_relative_to(widget)
		self.column_menu.show_all()
	
	def do_filter(self, widget):
		""" Callback for filtering; basically just delegate to the actual filter
		"""
		print("filtering...", self.search.get_text(), self.mod_only.get_active())
		self.store_filter.refilter()

	def do_close(self, *args):
		""" Callback for Close-button; check whether there are changes, if so
		update passwords and save file (save_encrypt creates backup)
		"""
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
		""" Callback for creating a new Password entry
		"""
		if ask_dialog(self.window, "Add Password"):
			print("adding password")
			vals = [*pwdmgr_model.ATTRIBUTES, -1, COLOR_NEW, False]
			self.store.append(vals)
	
	def do_remove(self, widget):
		""" Callback for removing the selected Password entry
		"""
		model, it = self.select.get_selected()
		if it is not None and ask_dialog(self.window, "Delete Selected?", 
				"Mark/unmark selected passwort for deletion?"):
			print("setting delete mark")
			vals = model[it]
			vals[IDX_DEL] ^= True
			self.set_color(vals)
	
	def filter_func(self, model, it, data):
		""" Callback called for each row in the table to determine whether it
		should be shown or hidden
		"""
		vals = model[it]
		if self.mod_only.get_active() and vals[IDX_COL] == COLOR_NON:
			return False
		s = self.search.get_text().lower()
		return any(s in att.lower() for att in vals[:N_ATT])
		
	def create_edit_func(self, column):
		""" Helper function for creating edit-callbacks for each column
		"""
		def edited(widget, path, text):
			values = self.store_filter[path]
			values[column] = text
			self.set_color(values)
		return edited
		
	def create_model(self):
		""" Create list model and filter model and populate with Passwords
		data format: [main Password attributes, index / ID, Color, Deleted?]
		"""
		self.store = Gtk.ListStore(*[str]*8 + [int, str, bool])
		for i, entry in enumerate(self.conf.passwords):
			vals = [*entry.values(), i, COLOR_NON, False]
			self.store.append(vals)
		self.store_filter = self.store.filter_new()
		self.store_filter.set_visible_func(self.filter_func)
	
	def create_table(self):
		""" Create the actual Tree View with columns for the Password attributes
		that can be edited and filtered in a scrolled container
		"""
		table = Gtk.TreeView.new_with_model(self.store_filter)
		self.select = table.get_selection()
		
		table.append_column(Gtk.TreeViewColumn("id", Gtk.CellRendererText(), text=IDX_ID, background=IDX_COL))
		for i, att in enumerate(pwdmgr_model.ATTRIBUTES):
			renderer = Gtk.CellRendererText()
			renderer.set_property("editable", True)
			renderer.connect("edited", self.create_edit_func(i))
			table.append_column(Gtk.TreeViewColumn(att, renderer, text=i, background=IDX_COL))
		
		return table
	
	def create_column_menu(self):
		""" Create Popover menu with checkbox buttons for toggling the different
		table columns on and off (and indirectly for reordering them)
		"""
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		for column in self.table.get_columns():
			if column.get_title() == "id": continue
			
			button = Gtk.CheckButton.new_with_label(column.get_title())
			button.set_active(True)
			def toggled(button=button, column=column):
				if button.get_active():
					self.table.append_column(column)
				else:
					self.table.remove_column(column)
			button.connect("toggled", toggled)
			vbox.pack_start(button, False, True, 10)
		
		menu = Gtk.Popover()
		menu.add(vbox)
		menu.set_position(Gtk.PositionType.BOTTOM)
		return menu
	
	def set_color(self, values):
		""" Set row color depending on whether the Password is marked for
		deletion, newly created, modified, or none of all that.
		"""
		values[IDX_COL] = (COLOR_DEL if values[IDX_DEL]
		              else COLOR_NEW if values[IDX_ID] == -1
		              else COLOR_MOD if values[:N_ATT] != self.conf.passwords[values[IDX_ID]].values()
		              else COLOR_NON)
		
		
def create_button(title, command, is_icon=True):
	""" Helper function for creating a GTK button with icon and callback
	"""
	button = Gtk.Button.new_from_icon_name(title, Gtk.IconSize.BUTTON) \
	         if is_icon else Gtk.Button.new_with_label(title)
	button.connect("clicked", command)
	button.set_property("relief", Gtk.ReliefStyle.NONE)
	return button

def ask_dialog(parent, title, message=None):
	""" Helper method for opening a simple yes/no dialog and getting the answer
	"""
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
