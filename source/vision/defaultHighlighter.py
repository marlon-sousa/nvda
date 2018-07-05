#vision/defaultHighlighter.py
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2018 NV Access Limited, Babbage B.V.

"""Default highlighter based on wx."""

from . import *
import wx
import gui
import api
from ctypes.wintypes import COLORREF
import winUser
from logHandler import log
from mouseHandler import getTotalWidthAndHeightAndMinimumPosition
from colors.predefined import *

class DefaultHighlighter(Highlighter):
	name = "defaultHighlighter"
	supportedContexts = frozenset([CONTEXT_FOCUS, CONTEXT_NAVIGATOR, CONTEXT_CARET])
	contextColors = {
		CONTEXT_FOCUS: red,
		CONTEXT_NAVIGATOR: blue, 
		CONTEXT_CARET: green
	}
	margin = 15

	def __init__(self, *roles):
		self.window = None
		super(Highlighter, self).__init__(*roles)

	def initializeHighlighter(self):
		super(DefaultHighlighter, self).initializeHighlighter()
		self.window = HighlightWindow(self)

	def terminateHighlighter(self):
		if self.window:
			self.window.Destroy()
			self.window = None
		super(DefaultHighlighter, self).terminateHighlighter()

	def updateContextRect(self, context, rect=None, obj=None):
		super(DefaultHighlighter, self).updateContextRect(context, rect, obj)
		self.refresh()

	def refresh(self):
		# Trigger a refresh of the highlight window, which will call onPaint
		if self.window:
			self.window.Refresh()

	def onPaint(self, event):
		window= event.GetEventObject()
		dc = wx.PaintDC(window)
		dc.SetBackground(wx.TRANSPARENT_BRUSH)
		dc.Clear()
		dc.SetBrush(wx.TRANSPARENT_BRUSH)
		for context in self.supportedContexts:
			rect = self.contextToRectMap.get(context)
			if not rect:
				continue
			dc.SetPen(wx.Pen(self.contextColors[context], 4))
			l, t, r, b = rect
			l -= self.margin
			t -= self.margin
			w = r - l + self.margin
			h = b - t + self.margin
			dc.DrawRectangle(l, t, w, h)

class HighlightWindow(wx.Frame):
	transparency = 0xC0

	def updateLocationForDisplays(self):
		displays = [ wx.Display(i).GetGeometry() for i in xrange(wx.Display.GetCount()) ]
		screenWidth, screenHeight, minPos = getTotalWidthAndHeightAndMinimumPosition(displays)
		self.SetPosition(minPos)
		self.SetSize((screenWidth, screenHeight))

	def __init__(self, highlighter):
		super(HighlightWindow, self).__init__(gui.mainFrame, style=wx.NO_BORDER | wx.STAY_ON_TOP | wx.FULL_REPAINT_ON_RESIZE | wx.FRAME_NO_TASKBAR)
		self.updateLocationForDisplays()
		self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
		exstyle = winUser.getExtendedWindowStyle(self.Handle) | winUser.WS_EX_LAYERED
		winUser.setExtendedWindowStyle(self.Handle, exstyle)
		winUser.SetLayeredWindowAttributes(self.Handle, 0, self.transparency, winUser.LWA_ALPHA | winUser.LWA_COLORKEY)
		self.Bind(wx.EVT_PAINT, highlighter.onPaint)
		self.Disable()
		self.Show()

