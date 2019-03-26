#!/usr/bin/env python
import random
import pyperclip as pyclip
import tkinter as tk
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


class LandFrame(tk.Frame):

	def __init__(self, master, land_type):
		tk.Frame.__init__(self, master)
		self.master = master
		self.land_type = land_type

		self.land_list = list(LANDS[land_type].keys())
		self.land_images = {}

		for land, path in LANDS[land_type].items():
			image = Image.open(path).resize((256, 359), resample=Image.LANCZOS)
			self.land_images[land] = ImageTk.PhotoImage(image)

		self.image_container = ttk.Label(self)
		self.image_container.grid(row=0, column=0, sticky='s', padx=10, pady=10)

		self.land_info = tk.StringVar(self)
		self.land_info.trace('w', lambda *_: self.set_land_image())
		self.land_info.set(random.choice(list(self.land_images)))

		self.land_dropdown = ttk.Combobox(self, width=20, textvariable=self.land_info, values=self.land_list, state='readonly')
		self.land_dropdown.grid(row=1, column=0, sticky='w', padx=15, pady=10)

		self.prev_button = ttk.Button(self, text='Prev', width=6, command=self.set_to_prev)
		self.prev_button.grid(row=1, column=0, sticky='e', padx=65)

		self.next_button = ttk.Button(self, text='Next', width=6, command=self.set_to_next)
		self.next_button.grid(row=1, column=0, sticky='e', padx=15)


	def set_land_image(self):
		self.image_container.config(image=self.land_images[self.land_info.get()])
		self.event_generate('<<LandChange>>')
		

	def enable(self):
		for widget in self.winfo_children():
			if widget.winfo_name() == '!combobox':
				widget.config(state='readonly')
			else:
				widget.config(state='normal')


	def disable(self):
		for widget in self.winfo_children():
			widget.config(state='disabled')


	def set_to_next(self):
		index = self.land_list.index(self.land_info.get())
		if (index + 1) >= len(self.land_list):
			self.land_info.set(self.land_list[0])
		else:
			self.land_info.set(self.land_list[index + 1])


	def set_to_prev(self):
		index = self.land_list.index(self.land_info.get())
		if index == 0:
			self.land_info.set(self.land_list[len(self.land_list) - 1])
		else:
			self.land_info.set(self.land_list[index - 1])


class LandSwap(tk.Tk):

	max_decklist_lines = 250

	background_colors = {
		'default': '#ffffff',
		'invalid': '#ffb6b6'
	}

	highlight_colors = {
		'Plains': '#fcfcc1',
		'Island': '#aeddf9',
		'Swamp': '#c2c2c2',
		'Mountain': '#ffb6b6',
		'Forest': '#94e9bc',
		'invalid': '#fb7676'
	}

	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)

		self.resizable(False, False)

		# DECKLIST

		self.decklist_frame = tk.Frame(self)
		self.decklist_frame.pack(side='left', padx=10, pady=10)

		self.decklist_import_button = ttk.Button(self.decklist_frame, text='Import decklist', width=15, command=self.import_decklist)
		self.decklist_import_button.grid(row=0, column=0, sticky='w', padx=5, pady=5)

		self.clear_button = ttk.Button(self.decklist_frame, text='Clear', width=7, command=self.clear_text)
		self.clear_button.grid(row=0, column=0, sticky='e', padx=5, pady=5)

		self.copy_clipboard_button = ttk.Button(self.decklist_frame, text='Copy to clipboard', width=17, command=self.copy_to_clipboard)
		self.copy_clipboard_button.grid(row=0, column=1, sticky='e', padx=5, pady=5)

		self.text_box = ModifiedText(self.decklist_frame, relief='flat', width=40, height=25, wrap='word')
		self.text_box.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
		self.text_box.tag_config('invalid', background=self.highlight_colors['invalid'])
		self.text_box.bind('<<TextModified>>', self.on_text_modified)
		self.text_box.bind_all('<<LandChange>>', self.on_land_change)

		for land_type, color in self.highlight_colors.items():
			self.text_box.tag_config(land_type, background=color)

		self.set_state('disabled', self.clear_button, self.copy_clipboard_button, self.text_box)

		# LANDS

		self.land_frames = {
			'Plains': LandFrame(self, 'Plains'),
			'Island': LandFrame(self, 'Island'),
			'Swamp': LandFrame(self, 'Swamp'),
			'Mountain': LandFrame(self, 'Mountain'),
			'Forest': LandFrame(self, 'Forest')
		}

		for frame in self.land_frames.values():
			frame.pack(side='left')
			frame.disable()


	def import_decklist(self):
		clipboard = pyclip.paste()
		if not clipboard:
			print('No text found on clipboard')
			return

		# DECKLIST VALIDATON

		print('Importing from clipboard...')

		self.text_box.config(state='normal')
		self.text_box.delete('1.0', 'end')
		self.text_box.insert('end', clipboard)

		line_count = int(self.text_box.index('end-1c').split('.')[0])

		if line_count > self.max_decklist_lines:
			self.on_import_failed('Aborting: Maximum length exceeded (%d lines)' % self.max_decklist_lines)
			return

		valid_line_re = r'^\s*$|^\d+\s(?:\S+\s)+\([A-Z0-9]{3}\)\s[A-Z0-9]{1,3}\s*$'
		invalid_line_count = 0
		current_line = 1

		while current_line <= line_count:
			search_index = '%d.0' % current_line
			if search_index == self.text_box.index('end-1c'):
				# Don't bother searching last line if blank
				break
			valid_index = self.text_box.search(valid_line_re, search_index, stopindex=search_index + ' lineend', regexp=True)
			if not valid_index:
				self.text_box.tag_add('invalid', search_index, search_index + ' lineend+1c')
				self.text_box.mark_set('invalid', search_index)
				self.text_box.see('invalid')
				invalid_line_count += 1

			current_line += 1

		if invalid_line_count:
			self.on_import_failed('Aborting: Found (%d) invalid lines' % invalid_line_count)
			return

		print('Decklist imported successfully')
		print('Searching for basic lands...')

		# SEARCH FOR LANDS

		land_found = False

		for land_type in LANDS:
			for land in LANDS[land_type]:
				pos = self.text_box.search(land, '1.0', stopindex='end')
				if pos:
					if not land_found:
						land_found = True

					self.text_box.mark_set(land_type, pos)
					self.text_box.mark_gravity(land_type, 'left')
					self.text_box.tag_add(land_type, pos + ' linestart', pos + ' lineend+1c')

					self.land_frames[land_type].land_info.set(land)
					self.land_frames[land_type].enable()
					
					print('Land found: %s' % land)
					break

		print('Finished search')

		if not land_found:
			print('No basic lands found')

		self.text_box.config(state='disabled')
		self.text_box.focus_set()


	def on_import_failed(self, message):
		print(message)
		self.text_box.config(background=self.background_colors['invalid'])
		self.text_box.config(state='disabled')
		self.text_box.focus_set()


	def clear_text(self):
		self.text_box.config(state='normal')
		self.text_box.delete('1.0', 'end')
		self.text_box.config(background=self.background_colors['default'])
		self.text_box.config(state='disabled')
		self.text_box.focus_set()

		for frame in self.land_frames.values():
			frame.disable()

		print('Decklist field cleared')
			

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
		if self.text_box.compare('end-1c', '==', '1.0'):
			self.set_state('disabled', self.clear_button, self.copy_clipboard_button)
			self.decklist_import_button.config(state='normal')
		else:
			self.set_state('normal', self.clear_button, self.copy_clipboard_button)
			self.decklist_import_button.config(state='disabled')


	def on_land_change(self, event):
		# Do nothing if text box is empty
		if self.text_box.compare('end-1c', '==', '1.0'):
			return
		land_type = event.widget.land_type
		land = event.widget.land_info
		
		self.text_box.config(state='normal')
		self.text_box.delete(land_type, land_type + ' lineend-1c')
		self.text_box.insert(land_type, land.get())
		self.text_box.config(state='disabled')
		self.text_box.see(land_type)


def main():
	land_swap = LandSwap()
	land_swap.title('MTGA Basic Land Swapper')
	land_swap.mainloop()


if __name__ == '__main__':
	main()
