#vision/defaultHighlighter.py
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2018 NV Access Limited, Babbage B.V.

"""Default highlighter based on wx."""

from . import Highlighter, CONTEXT_FOCUS, CONTEXT_NAVIGATOR, CONTEXT_CARET
import wx
import gui
import api
from ctypes.wintypes import COLORREF
import winUser
from logHandler import log
from mouseHandler import getTotalWidthAndHeightAndMinimumPosition
import cursorManager
from locationHelper import RectLTRB

class DefaultHighlighter(Highlighter):
	name = "defaultHighlighter"
	# Translators: Description for NVDA's built-in screen highlighter.
	description = _("Default")
	supportedContexts = frozenset([CONTEXT_FOCUS, CONTEXT_NAVIGATOR, CONTEXT_CARET])
	_contextColors = {
		CONTEXT_FOCUS: wx.RED,
		CONTEXT_NAVIGATOR: wx.BLUE,
		CONTEXT_CARET: wx.GREEN,
	}
	_highlightMargin = 15
	_refreshInterval = 250

	def _get__currentCaretIsVirtual(self):
		return isinstance(api.getCaretObject(), cursorManager.CursorManager)

	def __init__(self, *roles):
		self.window = None
		self._refreshTimer = None
		super(Highlighter, self).__init__(*roles)

	def initializeHighlighter(self):
		super(DefaultHighlighter, self).initializeHighlighter()
		self.window = HighlightWindow(self)
		self._refreshTimer = gui.NonReEntrantTimer(self.refresh)
		self._refreshTimer.Start(self._refreshInterval)

	def terminateHighlighter(self):
		if self._refreshTimer:
			self._refreshTimer.Stop()
			self._refreshTimer = None
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
			dc.SetPen(wx.Pen(self._contextColors[context], 4))
			rect = rect.expandOrShrink(self._highlightMargin).toClient(window.Handle).toLogical(window.Handle)
			if context == CONTEXT_CARET:
				if self._currentCaretIsVirtual:
					dc.DrawLine(rect.right, rect.top, rect.right, rect.bottom)
			else:
				dc.DrawRectangle(*rect.toLTWH())

class HighlightWindow(wx.Frame):
	transparency = 0xC0

	def updateLocationForDisplays(self):
		displays = [ wx.Display(i).GetGeometry() for i in xrange(wx.Display.GetCount()) ]
		screenWidth, screenHeight, minPos = getTotalWidthAndHeightAndMinimumPosition(displays)
		self.SetPosition(minPos)
		self.SetSize(self.scaleSize((screenWidth, screenHeight)))

	@property
	def scaleFactor(self):
		import windowUtils
		return windowUtils.getWindowScalingFactor(self.Handle)

	def scaleSize(self, size):
		"""Helper method to scale a size using the logical DPI
		@param size: The size (x,y) as a tuple or a single numerical type to scale
		@returns: The scaled size, returned as the same type"""
		if isinstance(size, tuple):
			return (self.scaleFactor * size[0], self.scaleFactor * size[1])
		return self.scaleFactor * size

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
