#!/usr/bin/env python
import os
import re
import random
import pyperclip as pyclip
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from PIL import ImageTk, Image

from lands import LANDS


class ModifiedText(ScrolledText):

	def __init__(self, *args, **kwargs):
		ScrolledText.__init__(self, *args, **kwargs)

		self._orig = self._w + '_orig'
		self.tk.call('rename', self._w, self._orig)
		self.tk.createcommand(self._w, self._proxy)

	def _proxy(self, command, *args):
		cmd = (self._orig, command) + args
		try:
			result = self.tk.call(cmd)
		except Exception:
			return None

		if command in ('insert', 'delete', 'replace'):
			self.event_generate('<<TextModified>>')

		return result


class LandFrame(Frame):
	
	images = {}

	def __init__(self, master, land_type):
		Frame.__init__(self, master)
		self.master = master
		self.land_type = land_type

		master.land_frames[land_type] = self

		for land, path in LANDS[land_type].items():
			image = Image.open(path).resize((256, 359), resample=Image.LANCZOS)
			self.images[land] = ImageTk.PhotoImage(image)

		self.land_list = list(self.images.keys())
		self.image_container = ttk.Label(self)

		self.land_var = StringVar(self)
		self.land_var.trace('w', lambda *_: master.on_land_change(self.land_var, land_type))
		self.land_var.set(random.choice(list(LANDS[land_type])))

		self.image_container.config(image=self.images[self.land_var.get()])
		self.image_container.grid(row=0, column=0, sticky=S, padx=10, pady=10)

		self.land_dropdown = ttk.Combobox(self, width=20, textvariable=self.land_var, values=self.land_list, state='readonly')
		self.land_dropdown.grid(row=1, column=0, sticky=W, padx=15, pady=10)

		self.prev_button = ttk.Button(self, text='Prev', width=6, command=lambda: master.set_to_prev(self.land_list, self.land_var, land_type))
		self.prev_button.grid(row=1, column=0, sticky=E, padx=65)

		self.next_button = ttk.Button(self, text='Next', width=6, command=lambda: master.set_to_next(self.land_list, self.land_var, land_type))
		self.next_button.grid(row=1, column=0, sticky=E, padx=15)


	def enable(self):
		self.image_container.config(state=NORMAL)
		self.land_dropdown.config(state='readonly')
		self.prev_button.config(state=NORMAL)
		self.next_button.config(state=NORMAL)


	def disable(self):
		for widget in self.winfo_children():
			widget.config(state=DISABLED)


class LandSwap(Tk):

	land_frames = {}
	max_decklist_chars = 100

	def __init__(self, *args, **kwargs):
		Tk.__init__(self, *args, **kwargs)

		self.resizable(False, False)

		# DECKLIST

		self.decklist_frame = Frame(self)
		self.decklist_frame.pack(side=LEFT, padx=10, pady=10)

		self.decklist_import_button = ttk.Button(self.decklist_frame, text='Import decklist', width=15, command=self.import_decklist)
		self.decklist_import_button.grid(row=0, column=0, sticky=W, padx=5, pady=5)

		self.clear_button = ttk.Button(self.decklist_frame, text='Clear', width=7, command=self.clear_text)
		self.clear_button.grid(row=0, column=0, sticky=E, padx=5, pady=5)

		self.copy_clipboard_button = ttk.Button(self.decklist_frame, text='Copy to clipboard', width=17, command=self.copy_to_clipboard)
		self.copy_clipboard_button.grid(row=0, column=1, sticky=E, padx=5, pady=5)

		self.text_box = ModifiedText(self.decklist_frame, relief=FLAT, width=40, height=25, wrap=WORD)
		self.text_box.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
		self.text_box.bind('<<TextModified>>', self.on_text_modified)

		self.set_state(DISABLED, self.clear_button, self.copy_clipboard_button, self.text_box)

		# LANDS

		self.plains_frame = LandFrame(self, 'Plains')
		self.plains_frame.pack(side=LEFT, padx=10, pady=10)
		self.plains_frame.disable()


	def import_decklist(self):
		self.set_state(NORMAL, self.text_box)
		self.text_box.insert(END, pyclip.paste())

		for land_type in LANDS:
			for land in LANDS[land_type]:
				pos = self.text_box.search(land, '1.0', stopindex=END)
				if pos:
					self.text_box.mark_set(land_type, pos)
					self.text_box.mark_gravity(land_type, LEFT)
					self.land_frames[land_type].land_var.set(land)
					self.land_frames[land_type].enable()
					break

		self.set_state(DISABLED, self.text_box, self.decklist_import_button)
		self.text_box.focus_set()


	def clear_text(self):
		self.set_state(NORMAL, self.text_box)
		self.text_box.delete('1.0', END)
		self.set_state(DISABLED, self.text_box)
		self.text_box.focus_set()

		for _, frame in self.land_frames.items():
			self.set_state(DISABLED, *frame.winfo_children())
			

	def copy_to_clipboard(self):
		string = self.text_box.get('1.0', 'end-1c')
		if not string:
			return
		pyclip.copy(string)
		print('Decklist copied to clipboard')


	def set_state(self, state, *widgets):
		for widget in widgets:
			widget.config(state=state)


	def on_text_modified(self, event):
		chars = len(event.widget.get('1.0', 'end-1c'))
		if chars == 0:
			self.set_state(DISABLED, self.decklist_import_button, self.clear_button, self.copy_clipboard_button)
			self.set_state(NORMAL, self.decklist_import_button)
		else:
			self.set_state(NORMAL, self.decklist_import_button, self.clear_button, self.copy_clipboard_button)
			self.set_state(DISABLED, self.decklist_import_button)


	def on_land_change(self, land, land_type):
		frame = self.land_frames[land_type]
		frame.image_container.config(image=frame.images[land.get()])

		self.text_box.config(state=NORMAL)
		self.text_box.delete(land_type, land_type + ' lineend')
		self.text_box.insert(land_type, land.get())
		self.text_box.config(state=DISABLED)


	def set_to_next(self, land_list, land, land_type):
		index = land_list.index(land.get())

		if (index + 1) >= len(land_list):
			land.set(land_list[0])
		else:
			land.set(land_list[index + 1])


	def set_to_prev(self, land_list, land, land_type):
		index = land_list.index(land.get())

		if index == 0:
			land.set(land_list[len(land_list) - 1])
		else:
			land.set(land_list[index - 1])


def main():
	land_swap = LandSwap()
	land_swap.title('MTGA Basic Land Swapper')
	land_swap.mainloop()


if __name__ == '__main__':
	main()
