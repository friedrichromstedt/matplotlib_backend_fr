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

# Last changed: 2010 Mar 11
# Developed since: Jul 2008
# File version: 0.1.0b

import matplotlib.figure
import matplotlib.backends.backend_agg
import matplotlib.backends.backend_ps

# Try to import PIL ...

try:
	import Image
except:
	# PIL will not be available for rendering to image formats like .png .
	pass

class FigureAxes:
	"""Abstraction layer of an axes and a figure both together."""

	def __init__(self, 
			figure = None, 
			left = 0.2, bottom = 0.2, width = 0.6, height = 0.6,
			axes = None,
			polar = None,
			autoscaling = None):
		"""FIGURE is the matplotlib.figure.Figure instance where to act on.
		AXES is optionally an existing axes instance.  If AXES is not given,
		a new axes instance will be created, either a cartesian, or a polar if
		POLAR is True.  Autoscaling will be turned on by default, if not
		overridded by AUTOSCALING.  If FIGURE is not given, it will be created
		and be initialised to be held and of size (1, 1) inches."""
	
		if autoscaling is None:
			autoscaling = True

		if figure is None:
			figure = matplotlib.figure.Figure(frameon = False)
			figure.hold(True)
			figure.set_size_inches(1, 1)

		# Initialise attributes ...

		self.layers = []
		self.drawn_layers = []
		self.needs_reset = False

		self.figure = figure
		
		if axes is None:
			# Create a new axes instance.
			self.axes = self.figure.add_axes(
					(left, bottom, width, height),
					polar = polar)

		else:
			# Take over the axes.
			self.axes = axes

		# Initialise the title etc. to some values.
		self.title = None
		self.xlabel = None
		self.ylabel = None
		
		# Turn autoscaling on.
		self.set_autoscale_on(autoscaling)
	
	def set_title(self, title):
		self.axes.set_title(title)
		self.title = title

	def set_xlabel(self, xlabel):
		self.axes.set_xlabel(xlabel)
		self.xlabel = xlabel

	def set_ylabel(self, ylabel):
		self.axes.set_ylabel(ylabel)
		self.ylabel = ylabel

	def set_xlim(self, lim):
		if lim is not None:
			self.set_autoscale_on(False)
			self.axes.set_xlim(lim)
		self.xlim = lim

	def set_ylim(self, lim):
		if lim is not None:
			self.set_autoscale_on(False)
			self.axes.set_ylim(lim)
		self.ylim = lim

	def get_xlim(self):
		return self.axes.get_xlim()

	def get_ylim(self):
		return self.axes.get_ylim()

	def set_autoscale_on(self, autoscale_on):
		self.axes.set_autoscale_on(autoscale_on)
		if autoscale_on:
			self.set_xlim(None)
			self.set_ylim(None)
			self.axes.autoscale_view()
		self.autoscale_on = autoscale_on

	def clear(self):
		self.axes.clear()
		self.set_title(self.title)
		self.set_xlabel(self.xlabel)
		self.set_ylabel(self.ylabel)
		self.set_xlim(self.xlim)
		self.set_ylim(self.ylim)

	def to_image(self, shape):
		dpi = self.figure.dpi
		self.figure.set_size_inches(
				float(shape[0]) / dpi,
				float(shape[1]) / dpi)

		agg_figure_container = matplotlib.backends.backend_agg.\
				FigureCanvasAgg(self.figure)
		agg_figure_container.draw()
		image_string = agg_figure_container.tostring_rgb()

		image = Image.fromstring("RGB", shape, image_string)
		return image

	def to_image_file(self, filename, shape):
		im = self.to_image(shape)
		im.save(filename)

	def to_eps_file(self, filename, shape):
		self.figure.set_size_inches(shape[0], shape[1])

		ps_figure_container = matplotlib.backends.backend_ps.\
				FigureCanvasPS(self.figure)
		ps_figure_container.print_eps(
				outfile = filename,
				dpi = self.figure.dpi)
