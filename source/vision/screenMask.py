#vision/screenMask.py
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2018 NV Access Limited

"""Screen mask/curtain implementation based on a wx overlay window."""

from . import ColorEnhancer, ColorTransformation
import wx
import gui
import api
# NVDA's built-in colors module is compatible with wx colors
import colors.predefined

class ScreenMask(ColorEnhancer):
	name = "screenMask"
	availableTransformations = (
		ColorTransformation("black", colors.predefined.black.name, colors.predefined.black)
	)

	def __init__(self, *roles):
		self.window = None
		self.timer = None
		super(ScreenMask, self).__init__(*roles)

	def initializeColorEnhancer(self):
		super(ScreenMask, self).initializeColorEnhancer()
		self.window = wx.Frame(parent=gui.mainFrame, id=wx.ID_ANY, pos=(0,0), size=api.getDesktopObject().location[2:], style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP)
		self.window.SetBackgroundColour(wx.BLUE)
		self.timer = wx.PyTimer(self.refresh)
		self.timer.Start(16)
		self.window.Disable()
		self.window.Show()

	def terminateColorEnhancer(self):
		if self.timer:
			self.timer.Stop()
			self.timer = None
		if self.window:
			self.window.Hide()
			self.window.Destroy()
			self.window = None
		super(ScreenMask, self).terminateColorEnhancer()

	def refresh(self):
		"""Refresh wrapper that gracefully handles the case that the mainframe gets destroyed."""
		if self.window:
			self.window.Refresh()
		else:
			self.timer.Stop()