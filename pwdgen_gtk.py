#!/usr/bin/env python3
# -*- coding: utf8 -*-


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

import pwdgen

class PwdGenFrame:
	
	def __init__(self, is_main=True):
		
		# create toggle buttons, number spinner, password entry and button
		self.toggle_abc = self.create_toggle("abc", True)
		self.toggle_ABC = self.create_toggle("ABC", True)
		self.toggle_123 = self.create_toggle("123", True)
		self.toggle_pct = self.create_toggle("$%&", False)
		self.number = Gtk.SpinButton.new_with_range(5, 50, 1)
		self.number.set_value(16)
		self.number.connect("value-changed", self.do_generate)
		self.password = Gtk.Entry.new()
		button = Gtk.Button.new_with_label("New")
		button.connect("clicked", self.do_generate)
		
		# create initial password
		self.do_generate()

		# assemble grid
		grid = Gtk.Grid.new()
		for i, w in enumerate((self.toggle_abc, self.toggle_ABC, self.toggle_123,
		                       self.toggle_pct, self.number)):
			grid.attach(w, i, 0, 1, 1)
		grid.attach(button, 0, 1, 1, 1)
		grid.attach(self.password, 1, 1, 4, 1)

		# put it all together in a window
		self.window = Gtk.ApplicationWindow(title=f"Password Generator")
		self.window.add(grid)
		self.window.show_all()
		if is_main:
			self.window.connect("destroy", Gtk.main_quit)
	
	def create_toggle(self, label, active):
		toggle = Gtk.ToggleButton.new_with_label(label)
		toggle.set_active(active)
		toggle.connect("toggled", self.do_generate)
		return toggle
	
	def do_generate(self, widget=None):
		num = int(self.number.get_value())
		lower = self.toggle_abc.get_active()
		upper = self.toggle_ABC.get_active()
		digit = self.toggle_123.get_active()
		punct = self.toggle_pct.get_active()
		if any((lower, upper, digit, punct)):
			p = pwdgen.generate(num, lower, upper, digit, punct)
		else:
			p = "Please select at least one group!"
		self.password.set_text(p)


if __name__ == "__main__":
	PwdGenFrame()
	Gtk.main()
