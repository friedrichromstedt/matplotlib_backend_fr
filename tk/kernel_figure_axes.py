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
# Developed since: Mar 2010
# File version: 0.1.0b

# Try to support several output formats ...

try:
	import Image
except:
	pass

import matplotlib_backend_fr.tk.panel_figure_axes


class KernelFigureAxes:
	"""Performs printing and scaling of a figure."""

	def __init__(self, master, figure_axes, shape = None):
		"""FIGURE_AXES is an matplotlib_backend_fr.figure_axes.FigureAxes 
		instance.  SHAPE is the initial shape of the panel."""

		self.master = master
		self.figure_axes = figure_axes
		self.panel = matplotlib_backend_fr.tk.panel_figure_axes.\
				PanelFigureAxes(
					master = master,
					event_handler_start_zoom = self.start_zoom,
					event_handler_zoom = self.zoom,
					event_handler_start_pan = self.start_pan,
					event_handler_pan = self.pan,
					event_handler_doubleclick_left = self.autozoom,
					event_handler_doubleclick_right = self.open_settings_dialog,
					image_generator = self.figure_axes.to_image,
					shape = shape)

	def update(self):
		self.panel.update()

	def _map_to_axes_coords(self, disp_coords):
		bbox = self.figure_axes.axes.get_position()
		axes_position = \
				(bbox.x0, bbox.y0, bbox.size[0], bbox.size[1]) # (l,b,w,h)
		return ((disp_coords[0] - axes_position[0]) / axes_position[2],
				(disp_coords[1] - axes_position[1]) / axes_position[3])
	
	def _map_to_data_coords(self, axes_coords):
		lims = [self.figure_axes.get_xlim(), self.figure_axes.get_ylim()]
		return (lims[0][0] + (lims[0][1] - lims[0][0]) * axes_coords[0],
				lims[1][0] + (lims[1][1] - lims[1][0]) * axes_coords[1])

	def start_zoom(self, disp_coords):
		"""Initialse zooming with DISP_COORDS invariant."""

		lims = [self.figure_axes.get_xlim(), self.figure_axes.get_ylim()]
		bbox = self.figure_axes.axes.get_position()
		axes_position = \
				(bbox.x0,bbox.y0, bbox.size[0], bbox.size[1]) # (l,b,w,h)
		axes_coords = self._map_to_axes_coords(disp_coords)
		self.zoom_start_position = self._map_to_data_coords(axes_coords)
		self.zoom_original_distances=(
				[lims[0][0] - self.zoom_start_position[0],
				 lims[0][1] - self.zoom_start_position[0]],
				[lims[1][0] - self.zoom_start_position[1],
				 lims[1][1] - self.zoom_start_position[1]])

	def zoom(self, (zoomx, zoomy)):
		"""ZOOM with magnification (ZOOMX, ZOOMY)."""

		zoom_new_distances=(
				[self.zoom_original_distances[0][0] * zoomx,
				 self.zoom_original_distances[0][1]*zoomx],
				[self.zoom_original_distances[1][0] * zoomy,
				 self.zoom_original_distances[1][1]*zoomy])
		
		zoom_new_lims=(
				[self.zoom_start_position[0] + zoom_new_distances[0][0],
				 self.zoom_start_position[0] + zoom_new_distances[0][1]],
				[self.zoom_start_position[1] + zoom_new_distances[1][0],
				 self.zoom_start_position[1] + zoom_new_distances[1][1]])

		self.figure_axes.set_xlim(zoom_new_lims[0])
		self.figure_axes.set_ylim(zoom_new_lims[1])

	def start_pan(self):
		"""Start panning."""

		lims = \
				[list(self.figure_axes.get_xlim()),
				 list(self.figure_axes.get_ylim())]
		self.pan_start_lims=lims
		
		bbox = self.figure_axes.axes.get_position()
		axes_position = \
				(bbox.x0, bbox.y0, bbox.size[0], bbox.size[1]) # (l,b,w,h)
		self.pan_ratio=(
				(lims[0][1] - lims[0][0]) / axes_position[2],
				(lims[1][1] - lims[1][0]) / axes_position[3])

	def pan(self,compensate):
		"""Pan with COMPENSATE."""

		movement=(
				self.pan_ratio[0] * compensate[0],
				self.pan_ratio[1] * compensate[1])
		pan_new_lims=(
				[self.pan_start_lims[0][0] - movement[0],
				 self.pan_start_lims[0][1] - movement[0]],
				[self.pan_start_lims[1][0] - movement[1],
				 self.pan_start_lims[1][1] - movement[1]])
		self.figure_axes.set_xlim(pan_new_lims[0])
		self.figure_axes.set_ylim(pan_new_lims[1])

	def autozoom(self):
		"""Turn autozoom on."""

		self.figure_axes.set_autoscale_on(True)

	def open_settings_dialog(self):
		"""Open the settings dialog."""

		settingsdialog = matplotlib_backend_fr.tk.panel_figure_axes.\
				SettingsDialog(self.master, 
						figure_axes = self.figure_axes, 
						hook_save_eps = self.save_eps, 
						hook_save_img = self.save_img, 
						hook_update_figure_axes = self.update)

		if self.panel.pixelsize is not None:
			(xdim, ydim) = self.panel.pixelsize
			settingsdialog.img_xdim.set(xdim)
			settingsdialog.img_ydim.set(ydim)

	def save_eps(self, filename, shape):
		self.figure_axes.to_eps_file(filename, shape)

	def save_img(self, filename, shape):
		im = self.figure_axes.to_image_file(filename, shape)

	def destroy(self):
		self.panel.destroy()
