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

TODO (small ones; bigger ones are in Github Issues)
- scroll to newly created password (seems to be not so easy...)
- add "undo change" button?
- show changes on exit
- sort by drag&drop or sort by column?
"""

from collections import Counter

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import config
import pwdgen_gtk
import pwdmgr_core
import pwdmgr_model


# colors indicating the status of the Passwords
# pastel colors working equally well on light and dark theme
COLOR_NON = None       # neutral background, depends on theme
COLOR_NEW = "#aaffaa"  # pastel green for new entries
COLOR_DEL = "#ffaaaa"  # pastel red for deleted entries
COLOR_MOD = "#aaaaff"  # pastel blue for modified entries
COLOR_FGN = None       # neutral foreground, depends on theme
COLOR_FGB = "#000000"  # black, for pastel background

# indices for derived ID, fg- and bg-color, and deleted status
N_ATT = len(pwdmgr_model.ATTRIBUTES)
IDX_ID, IDX_FG, IDX_BG, IDX_DEL = N_ATT, N_ATT+1, N_ATT+2, N_ATT+3


class PwdMgrFrame:
	""" Wrapper-Class for the GTK window and all its elements (but not in itself
	a subclass of Window), including callback methods for different actions.
	"""

	def __init__(self, conf):
		""" Create Password Manager window for given config
		"""
		self.conf = conf
		try:
			self.original_passwords = pwdmgr_core.load_decrypt(self.conf)
		except FileNotFoundError:
			print("File not found... starting new list")
			self.original_passwords = []

		# create search and filtering widgets
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
		header.pack_start(create_button("Select Columns", self.do_filter_columns, is_icon=False), False, False, 0)
		header.pack_start(create_button("Tags", self.do_filter_tags, is_icon=False), False, False, 0)
		header.pack_start(create_button("Password Generator", self.do_genpwd, is_icon=False), False, False, 0)
		header.pack_end(create_button("list-remove", self.do_remove, "Mark selected for Removal"), False, False, 0)
		header.pack_end(create_button("list-add", self.do_add, "Add new Entry"), False, False, 0)

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
		self.window = Gtk.ApplicationWindow(title=f"Password Manager - {conf.filename}")
		self.window.resize(800, 600)
		self.window.connect("delete-event", self.do_close)
		self.window.connect("destroy", Gtk.main_quit)
		self.window.add(body)
		self.window.show_all()

	def do_filter_columns(self, widget):
		""" Callback for showing the column-filter menu; not the actual buttons
		"""
		self.column_menu.set_relative_to(widget)
		self.column_menu.show_all()

	def do_filter_tags(self, widget):
		""" Callback for showing the tag-filter menu; not the actual buttons
		Other than the Columns menu, the tags menu is created anew each time
		"""
		tag_menu = self.create_tags_menu()
		tag_menu.set_relative_to(widget)
		tag_menu.show_all()

	def do_filter(self, _widget):
		""" Callback for filtering; basically just delegate to the actual filter
		"""
		print("filtering...", self.search.get_text(), self.mod_only.get_active())
		self.store_filter.refilter()

	def do_close(self, *_args):
		""" Callback for Close-button; check whether there are changes, if so
		update passwords and save file (save_encrypt creates backup)
		"""
		new_passwords = [pwdmgr_model.Password(*vals[:N_ATT])
		                 for vals in self.store if not vals[IDX_DEL]]
		if new_passwords != self.original_passwords:
			if ask_dialog(self.window, "Save Changes?", "Select 'No' to review changes"):
				print("saving...")
				try:
					pwdmgr_core.save_encrypt(self.conf, new_passwords)
					return False
				except Exception as e:
					return not ask_dialog(self.window, f"Encryption failed:\n{e}\nExit Anyway?")
			else:
				return not ask_dialog(self.window, "Exit Anyway?")
		return False

	def do_add(self, _widget):
		""" Callback for creating a new Password entry
		"""
		if ask_dialog(self.window, "Add Password"):
			print("adding password")
			vals = [*pwdmgr_model.ATTRIBUTES, -1, None, None, False]
			self.set_color(vals)
			self.store.append(vals)

	def do_remove(self, _widget):
		""" Callback for removing the selected Password entry
		"""
		_, itr = self.select.get_selected()  # need unfiltered iter!
		if itr is not None and ask_dialog(self.window, "Delete Selected?",
				"Mark/unmark selected password for deletion?"):
			print("setting delete mark")
			itr = self.store_filter.convert_iter_to_child_iter(itr)
			vals = self.store[itr]
			vals[IDX_DEL] ^= True
			self.set_color(vals)

	def do_genpwd(self, _widget):
		"""Show Password Generator
		"""
		pwdgen_gtk.PwdGenFrame(is_main=False)

	def filter_func(self, model, itr, _data):
		""" Callback called for each row in the table to determine whether it
		should be shown or hidden
		"""
		vals = model[itr]
		if self.mod_only.get_active() and vals[IDX_BG] == COLOR_NON:
			return False
		text = self.search.get_text().lower()
		return any(text in att.lower() for att in vals[:N_ATT])

	def create_edit_func(self, column):
		""" Helper function for creating edit-callbacks for each column
		"""
		def edit_func(_widget, path, text):
			# get unfiltered path or Exception if edit removes row from filter
			path = Gtk.TreePath.new_from_string(path)
			path = self.store_filter.convert_path_to_child_path(path)
			values = self.store[path]
			values[column] = text
			self.set_color(values)
		return edit_func

	def create_model(self):
		""" Create list model and filter model and populate with Passwords
		data format: [main Password attributes, index / ID, Color, Deleted?]
		"""
		self.store = Gtk.ListStore(*[str]*8 + [int, str, str, bool])
		for i, entry in enumerate(self.original_passwords):
			vals = [*entry.values(), i, None, None, False]
			self.set_color(vals)
			self.store.append(vals)
		self.store_filter = self.store.filter_new()
		self.store_filter.set_visible_func(self.filter_func)

	def create_table(self):
		""" Create the actual Tree View with columns for the Password attributes
		that can be edited and filtered in a scrolled container
		"""
		table = Gtk.TreeView.new_with_model(self.store_filter)
		self.select = table.get_selection()

		table.append_column(Gtk.TreeViewColumn("id", Gtk.CellRendererText(), text=IDX_ID, foreground=IDX_FG, background=IDX_BG))
		for i, att in enumerate(pwdmgr_model.ATTRIBUTES):
			renderer = Gtk.CellRendererText()
			renderer.set_property("editable", True)
			renderer.connect("edited", self.create_edit_func(i))
			table.append_column(Gtk.TreeViewColumn(att, renderer, text=i, foreground=IDX_FG, background=IDX_BG))

		return table

	def create_column_menu(self):
		""" Create Popover menu with checkbox buttons for toggling the different
		table columns on and off (and indirectly for reordering them)
		"""
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		for column in self.table.get_columns():
			if column.get_title() == "id":
				continue

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

	def create_tags_menu(self):
		""" Create Popover menu with buttons for filtering by tags
		"""
		grid = Gtk.Grid()
		idx_tags = pwdmgr_model.ATTRIBUTES.index("tags")
		tags = Counter(tag.strip() for vals in self.store for tag in vals[idx_tags].split(","))
		for i, (tag, count) in enumerate(sorted(tags.most_common())):
			def clicked(*_args, tag=tag):
				self.search.set_text(tag)
			button = create_button(f"{tag} ({count})", clicked, is_icon=False)
			grid.attach(button, i // 10, i % 10, 1, 1)

		menu = Gtk.Popover()
		menu.add(grid)
		menu.set_position(Gtk.PositionType.BOTTOM)
		return menu

	def set_color(self, values):
		""" Set row color depending on whether the Password is marked for
		deletion, newly created, modified, or none of all that.
		"""
		values[IDX_BG] = (COLOR_DEL if values[IDX_DEL]
		              else COLOR_NEW if values[IDX_ID] == -1
		              else COLOR_MOD if values[:N_ATT] != self.original_passwords[values[IDX_ID]].values()
		              else COLOR_NON)
		values[IDX_FG] = COLOR_FGN if values[IDX_BG] == COLOR_NON else COLOR_FGB


def create_button(title, command, tooltip=None, is_icon=True):
	""" Helper function for creating a GTK button with icon and callback
	"""
	button = Gtk.Button.new_from_icon_name(title, Gtk.IconSize.BUTTON) \
	         if is_icon else Gtk.Button.new_with_label(title)
	button.connect("clicked", command)
	button.set_property("relief", Gtk.ReliefStyle.NONE)
	button.set_tooltip_text(tooltip)
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


def main():
	"""Run Password Manager UI
	"""
	conf = config.load_config()
	# ~conf = pwdmgr_model.create_test_config()
	print(f"Using {conf}")
	PwdMgrFrame(conf)
	Gtk.main()


if __name__ == "__main__":
	main()
