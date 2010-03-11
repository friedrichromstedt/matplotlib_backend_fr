# Copyright (c) 2009 Friedrich Romstedt <www.friedrichromstedt.org>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Last changed: 2009 Sep 6
# Developed since: Apr 2009
# File version: 0.1.11b

import types
import Tkinter

class Validity:
	def __init__(self,valid,value=None):
		self.valid=valid
		self.value=value

def number(str):
	try:
		value=eval(str)
		vtype=type(value)
		if vtype==types.IntType or vtype==types.FloatType or \
				vtype==types.LongType:
			return Validity(True,value)
		else:
			return Validity(False)
	except:
		return Validity(False)

def int(str):
	try:
		value=eval(str)
		vtype=type(value)
		if vtype==types.IntType or vtype==types.LongType:
			return Validity(True,value)
		else:
			return Validity(False)
	except:
		return Validity(False)

def string(str):
	return Validity(True,str)

def number_none(str):
	try:
		value=eval(str)
		if number(str).valid or value is None:
			return Validity(True,value)
		else:
			return Validity(False)
	except:
		return Validity(False)


class VEntry:
	def __init__(self,master,validate=None,initial='',formatter=None,
			hook_update=None,**entry_kwargs):
		self.var=Tkinter.StringVar(master)
		self.entry=Tkinter.Entry(master,textvariable=self.var,
				**entry_kwargs)
		if validate is None:
			validate=string
		if formatter is None:
			formatter=str
		self.validate_fn=validate
		self.hook_update=hook_update
		self.formatter=formatter

		self.initial=initial
		self.value=None

	def initialise(self, callback = True):
		self.entry.bind('<KeyRelease>', self.tk_key_release)
		self.var.set(self.formatter(self.initial))
		if not self.validate(callback = callback):
			raise ValueError('error in initialisation: initial value not valid')

	def tk_key_release(self, event):
		self.validate()
	
	def validate(self,callback=True):
		validity=self.validate_fn(self.var.get())
		if validity.valid:
			self.value=validity.value
			self.entry['background']='white'
			if self.hook_update is not None and callback:
				self.hook_update()
		else:
			self.entry['background']='orange'
		return validity.valid

	def set(self,value,callback=True):
		self.var.set(self.formatter(value))
		return self.validate(callback=callback)

	def get(self):
		return self.value

	def pack(self,*entry_args,**entry_kwargs):
		self.entry.pack(*entry_args,**entry_kwargs)
	
	def pack_forget(self):
		self.entry.pack_forget()

	def grid(self,*entry_args,**entry_kwargs):
		self.entry.grid(*entry_args,**entry_kwargs)

	def grid_forget(self):
		self.entry.grid_forget()

	def disable(self):
		self.entry['state']='disabled'

	def enable(self):
		self.entry['state']='normal'

	def destroy(self):
		self.entry.destroy()


class NamedVEntry(VEntry):
	def __init__(self,
			master, name=None, 
			column=None, row=None, mode='horizontal',
			validate=None, initial='', formatter=None,
			label=None,
			hook_update=None, **ventry_kwargs):
		VEntry.__init__(self,master,validate=validate,initial=initial,
				formatter=formatter,
				hook_update=hook_update,**ventry_kwargs)
		self.mode = mode
		if label is None:
			if name is None:
				raise ValueError('NAME must be specified if no LABEL is given.')
			self.label=Tkinter.Label(master,text=name)
		else:
			self.label=label

		if self.mode not in ('horizontal', 'vertical'):
			raise ValueError('mode must be "horizontal" or "vertical"')

		if row is not None and column is not None:
			self.grid(row=row, column=column)

	def pack(self, *args, **kwargs):
		raise NotImplementedError

	def pack_forget(self):
		raise NotImplementedError

	def grid(self, column, row, **ventry_kwargs):
		ventry_kwargs.setdefault('sticky', Tkinter.W)
		if self.mode=='horizontal':
			VEntry.grid(self,
					column = column + 1,
					row = row,
					**ventry_kwargs)
			self.label.grid(
					column = column,
					row = row,
					sticky = Tkinter.E)
		elif self.mode=='vertical':
			VEntry.grid(self,
					column = column,
					row = row + 1,
					**ventry_kwargs)
			self.label.grid(
					column = column,
					row = row,
					sticky = Tkinter.W)

	def grid_forget(self):
		VEntry.grid_forget(self)
		self.label.grid_forget()

	def destroy(self):
		self.label.destroy()
		VEntry.destroy(self)
