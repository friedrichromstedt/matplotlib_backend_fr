# Copyright (c) 2008, 2009, 2010 Friedrich Romstedt 
# <www.friedrichromstedt.org>
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

# Last changed: 2010 Jan 19
# Developed since: Aug 2008
# File version: 0.3.1b

import Tkinter
import ImageTk
import tkFileDialog
import matplotlib_backend_fr

# Allow updates for external ventry module ...

try:
	import ventry
except:
	# Use internal fallback (maybe not most recent).
	import matplotlib_backend_fr.ventry as ventry


class PanelFigureAxes:
	def __init__(self, master,
			event_handler_start_zoom, event_handler_zoom,
			event_handler_start_pan, event_handler_pan,
			event_handler_doubleclick_left,
			event_handler_doubleclick_right,
			image_generator,
			shape = None):

		if shape is None:
			shape = (200,200)

		self.event_handler_start_zoom = event_handler_start_zoom
		self.event_handler_zoom = event_handler_zoom
		self.event_handler_start_pan = event_handler_start_pan
		self.event_handler_pan = event_handler_pan
		self.event_handler_doubleclick_left = event_handler_doubleclick_left
		self.event_handler_doubleclick_right = event_handler_doubleclick_right
		self.image_generator = image_generator

		self.viewport,self.viewport_tag = None,None

		self.canvas = Tkinter.Canvas(master,
				highlightthickness = 0,
				background = 'white',
				width = shape[0],
				height = shape[1])

		self.canvas.pack(expand = True, fill = Tkinter.BOTH)
		self.canvas.bind('<Configure>', self.tk_configure)
		self.canvas.bind('<ButtonPress-1>', self.tk_press_left_button)
		self.canvas.bind('<ButtonPress-3>', self.tk_press_right_button)
		self.canvas.bind('<ButtonRelease-1>', self.tk_release_left_button)
		self.canvas.bind('<ButtonRelease-3>', self.tk_release_right_button)
		self.canvas.bind('<Motion>', self.tk_motion)
		self.canvas.bind('<Double-Button-1>', self.tk_double_left_button)
		self.canvas.bind('<Double-Button-3>', self.tk_double_right_button)
		self.pixelsize = None

		self.motion_origin = None
		self.zooming_origin = None
		self.zooming_initial_distances = None
		self.pan_cursor = None
		self.motion_mode = 'none'

	def map_to_display(self, (scrx, scry)):
		return (float(scrx) / self.pixelsize[0],
				1 - float(scry) / self.pixelsize[1])

	def tk_configure(self, event):
		self.pixelsize = (event.width, event.height)
		self.update()

	def tk_press_left_button(self, event):
		disp_coords = self.map_to_display((event.x, event.y))
		self.motion_origin = (event.x, event.y)
		self.motion_mode = 'zoom'
		self.zooming_origin = disp_coords
		self.event_handler_start_zoom(disp_coords)

	def tk_press_right_button(self, event):
		disp_coords = self.map_to_display((event.x, event.y))
		self.pan_origin = disp_coords
		self.motion_mode = 'pan'
		self.event_handler_start_pan()

	def tk_release_left_button(self, event):
		self.motion_mode = 'none'

	def tk_release_right_button(self, event):
		self.motion_mode = 'none'

	def tk_double_left_button(self, event):
		self.event_handler_doubleclick_left()
		self.update()

	def tk_double_right_button(self, event):
		self.event_handler_doubleclick_right()

	def tk_motion(self, event):
		if self.motion_mode == 'zoom':
			pixel_distances = (self.motion_origin[0] - event.x,
					event.y - self.motion_origin[1])
			factors=[(2.0 ** (pixel_distances[i] * 0.02)) for i in (0,1)]
			self.event_handler_zoom(factors)
			self.update()
		elif self.motion_mode == 'pan':
			disp_coords = self.map_to_display((event.x, event.y))
			compensate = [disp_coords[i] - self.pan_origin[i] for i in (0,1)]
			self.event_handler_pan(compensate)
			self.update()

	def update(self):
		if self.pixelsize is None: 
			return
		image = self.image_generator(self.pixelsize)
		(old_viewport, old_viewport_tag) = (self.viewport, self.viewport_tag)
		self.viewport = ImageTk.PhotoImage(image)
		self.viewport_tag = self.canvas.create_image((0,0), 
				image = self.viewport, anchor='nw')
		if old_viewport is not None and old_viewport_tag is not None:
			self.canvas.delete(old_viewport_tag)
		if not matplotlib_backend_fr.has_mainloop:
			self.canvas.update()
	
	def destroy(self):
		if self.viewport is not None and self.viewport_tag is not None:
			self.canvas.delete(self.viewport_tag)
		del self.viewport, self.viewport_tag
		self.canvas.destroy()
		del self.canvas


class SettingsDialog(Tkinter.Toplevel):
	def __init__(self, master,
			figure_axes,
			hook_update_figure_axes,
			hook_save_eps,
			hook_save_img):

		Tkinter.Toplevel.__init__(self, master)
		self.figure_axes = figure_axes
		self.hook_update_figure_axes = hook_update_figure_axes
		self.hook_save_eps = hook_save_eps
		self.hook_save_img = hook_save_img

		# Create Save widgets ...

		# Create structure frames.
		self.lframe_save = Tkinter.LabelFrame(self, text = 'Save')
		self.lframe_save.pack(side = Tkinter.LEFT, anchor = Tkinter.N)

		self.lframe_eps = Tkinter.LabelFrame(self.lframe_save, text = 'EPS')
		self.lframe_eps.pack(side = Tkinter.TOP)
		
		self.lframe_img = Tkinter.LabelFrame(self.lframe_save, text = 'Image')
		self.lframe_img.pack(side = Tkinter.TOP)


		# Create dimension input EPS.
		self.frame_eps_dim = Tkinter.Frame(self.lframe_eps)
		self.frame_eps_dim.pack(side = Tkinter.TOP)

		self.eps_xdim = ventry.NamedVEntry(self.frame_eps_dim,
				name = 'Size X (Inches):',
				column = 0, row = 0,
				initial = 9.0, validate = ventry.number)
		self.eps_ydim = ventry.NamedVEntry(self.frame_eps_dim,
				name = 'Size Y (Inches):',
				column = 0, row = 1,
				initial = 9.0, validate = ventry.number)
		self.eps_xdim.initialise()
		self.eps_ydim.initialise()

		# Create save button EPS.
		self.button_eps = Tkinter.Button(self.lframe_eps,
				text = 'Save ...',
				command = self.tk_save_eps)
		self.button_eps.pack(side = Tkinter.TOP, fill = Tkinter.X)


		# Create dimension input image.
		self.frame_img_dim = Tkinter.Frame(self.lframe_img)
		self.frame_img_dim.pack(side = Tkinter.TOP)

		self.img_xdim = ventry.NamedVEntry(self.frame_img_dim,
				name = 'Size X (Pixels):',
				column = 0, row = 0,
				initial = 800, validate = ventry.int)
		self.img_ydim = ventry.NamedVEntry(self.frame_img_dim,
				name = 'Size Y (Pixels):',
				column = 0,row = 1,
				initial = 600,validate = ventry.int)
		self.img_xdim.initialise()
		self.img_ydim.initialise()

		# Create save button image.
		self.button_img = Tkinter.Button(self.lframe_img,
				text = 'Save ...',
				command = self.tk_save_img)
		self.button_img.pack(side = Tkinter.TOP, fill = Tkinter.X)

		# Create Settings widgets ...

		self.lframe_settings = Tkinter.LabelFrame(self, text = 'Settings')
		self.lframe_settings.pack(side = Tkinter.LEFT, anchor = Tkinter.N)

		# Create labeling widgets.
		self.lframe_labeling = Tkinter.LabelFrame(self.lframe_settings,
				text = 'Labeling')
		self.lframe_labeling.pack(side = Tkinter.TOP, anchor = Tkinter.W)
		self.frame_labeling = Tkinter.Frame(self.lframe_labeling)
		self.frame_labeling.pack(side = Tkinter.TOP)
		
		if self.figure_axes.title is None:
			initial_title = ''
		else:
			initial_title = self.figure_axes.title

		if self.figure_axes.xlabel is None:
			initial_xlabel = ''
		else:
			initial_xlabel = self.figure_axes.xlabel

		if self.figure_axes.ylabel is None:
			initial_ylabel = ''
		else:
			initial_ylabel = self.figure_axes.ylabel

		self.title = ventry.NamedVEntry(self.frame_labeling,
				name = 'Title:',
				column = 0, row = 0,
				initial = initial_title,
				width = 40)
		self.xlabel = ventry.NamedVEntry(self.frame_labeling,
				name = 'x label:',
				column = 0, row = 1,
				initial = initial_xlabel,
				width = 40)
		self.ylabel = ventry.NamedVEntry(self.frame_labeling,
				name = 'y label:',
				column = 0, row = 2,
				initial = initial_ylabel,
				width = 40)
		self.title.initialise()
		self.xlabel.initialise()
		self.ylabel.initialise()

		self.update_title()

		self.button_update_labeling = Tkinter.Button(self.lframe_labeling,
				text = 'Update',
				command = self.tk_update_labeling)
		self.button_update_labeling.pack(side = Tkinter.TOP,
				fill = Tkinter.X)

		# Create limit widgets.
		self.lframe_limits = Tkinter.LabelFrame(self.lframe_settings,
				text = 'Limits')
		self.lframe_limits.pack(side = Tkinter.TOP, anchor = Tkinter.W)
		self.frame_limits = Tkinter.Frame(self.lframe_limits)
		self.frame_limits.pack(side = Tkinter.TOP)

		(xlim0, xlim1) = self.figure_axes.get_xlim()
		(ylim0, ylim1) = self.figure_axes.get_ylim()

		self.xlim_left = ventry.NamedVEntry(self.frame_limits,
				name = 'x limits:',
				column = 0, row = 0,
				initial = xlim0,
				validate = ventry.number)
		self.xlim_right = ventry.VEntry(self.frame_limits,
				initial = xlim1,
				validate = ventry.number)
		self.xlim_right.grid(column = 2, row = 0)
		self.xlim_left.initialise()
		self.xlim_right.initialise()

		self.ylim_bottom = ventry.NamedVEntry(self.frame_limits,
				name = 'y limits:',
				column = 0, row = 1,
				initial = ylim0,
				validate = ventry.number)
		self.ylim_top = ventry.VEntry(self.frame_limits,
				initial = ylim1,
				validate = ventry.number)
		self.ylim_top.grid(column = 2, row = 1)
		self.ylim_bottom.initialise()
		self.ylim_top.initialise()

		self.autoscale = Tkinter.BooleanVar(self.lframe_limits)
		self.autoscale.set(self.figure_axes.autoscale_on)
		self.checkbutton_autoscale = Tkinter.Checkbutton(self.lframe_limits,
				text = 'Autoscale',
				command = self.tk_autoscale,
				variable = self.autoscale)
		self.checkbutton_autoscale.pack(side = Tkinter.LEFT)

		self.button_update_limits = Tkinter.Button(self.lframe_limits,
				text = 'Update',
				command = self.tk_update_limits)
		self.button_update_limits.pack(side = Tkinter.TOP,
				fill = Tkinter.X)

		self.update_autoscale_accessibility()

	def tk_save_eps(self):
		filename = tkFileDialog.asksaveasfilename(
				defaultextension = '.eps',
				filetypes=[
						('Encapsulated PostScript', '*.eps'),
						('PostScript', '*.ps'),
						('Encapsulated PostScript', '*.epi'),
						('All Files', '*')],
				parent = self,
				title = 'Save Diagram as Encapsulated PostScript')
		if filename != '':
			self.hook_save_eps(filename,
					shape = (self.eps_xdim.get(), self.eps_ydim.get()))

	def tk_save_img(self):
		filename = tkFileDialog.asksaveasfilename(
				defaultextension = '.png',
				filetypes = [
						('Any Image File Format', '*'),
						('All Files', '*')],
				parent = self,
				title = 'Save Diagram as Image')
		if filename != '':
			self.hook_save_img(filename,
					shape = (self.img_xdim.get(), self.img_ydim.get()))

	def tk_update_labeling(self):
		self.figure_axes.set_title(self.title.get())
		self.figure_axes.set_xlabel(self.xlabel.get())
		self.figure_axes.set_ylabel(self.ylabel.get())

		self.hook_update_figure_axes()
		self.update_title()

	def tk_update_limits(self):
		if self.autoscale.get():
			
			# We are in autoscale mode, thus update the values displayed ...

			(xlim0, xlim1) = self.figure_axes.get_xlim()
			(ylim0, ylim1) = self.figure_axes.get_ylim()

			self.xlim_left.set(xlim0)
			self.xlim_right.set(xlim1)
			self.ylim_bottom.set(ylim0)
			self.ylim_top.set(ylim1)

		else:
			
			# We are in explicit mode, thus write the values typed in to
			# the figure_axes ...

			self.figure_axes.set_xlim(
					(self.xlim_left.get(), self.xlim_right.get()))
			self.figure_axes.set_ylim(
					(self.ylim_bottom.get(), self.ylim_top.get()))

			# Only in this branch update the figure_axes.
			self.hook_update_figure_axes()

	def update_autoscale_accessibility(self):
		"""Enables / Disables widgets according to the autoscale setting."""

		if self.autoscale.get():

			# Disable all controls ...

			self.xlim_left.disable()
			self.xlim_right.disable()
			self.ylim_bottom.disable()
			self.ylim_top.disable()
			
		else:

			# Enable all controls ...

			self.xlim_left.enable()
			self.xlim_right.enable()
			self.ylim_bottom.enable()
			self.ylim_top.enable()

	def tk_autoscale(self):
		"""Called on changes of the autoscale checkbutton."""

		# Update the figure_axes' settings ...

		if self.autoscale.get():
			self.figure_axes.set_autoscale_on(True)
		else:
			self.figure_axes.set_autoscale_on(False)

		# Enable / disable the controls ...

		self.update_autoscale_accessibility()

		# If the autoscaling has been disabled, update the limits
		# because they may have changed due to autoscaling under the way ...

		(xlim0, xlim1) = self.figure_axes.get_xlim()
		(ylim0, ylim1) = self.figure_axes.get_ylim()

		self.xlim_left.set(xlim0)
		self.xlim_right.set(xlim1)
		self.ylim_bottom.set(ylim0)
		self.ylim_top.set(ylim1)

		self.hook_update_figure_axes()

	def update_title(self):
		"""Update the title of the window according to the title of the
		figure_axes."""

		# Choose a title which is meaningful both if the title has been set
		# and also if not.
		self.wm_title('Diagram Settings ' + self.title.get())
