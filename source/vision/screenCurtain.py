#vision/screenCurtain.py
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2018 NV Access Limited

"""Screen curtain implementation based on the windows magnification API."""

from . import ColorEnhancer, ColorTransformation, ROLE_MAGNIFIER, ROLE_HIGHLIGHTER
import winVersion
try:
	import winMagnification
except AttributeError:
	if (winVersion.winVersion.major, winVersion.winVersion.minor) < (6, 2):
		raise RuntimeError("This module is only supported on Windows 8 and above")
	raise
from ctypes import byref

TRANSFORM_BLACK = winMagnification.MAGCOLOREFFECT()
TRANSFORM_BLACK.transform[4][4] = 1.0
TRANSFORM_DEFAULT = winMagnification.MAGCOLOREFFECT()
TRANSFORM_DEFAULT.transform[0][0] = 1.0
TRANSFORM_DEFAULT.transform[1][1] = 1.0
TRANSFORM_DEFAULT.transform[2][2] = 1.0
TRANSFORM_DEFAULT.transform[3][3] = 1.0
TRANSFORM_DEFAULT.transform[4][4] = 1.0

class WinMagnificationScreenCurtain(ColorEnhancer):
	"""Screen curtain implementation based on the windows magnification API.
	This is only supported on Windows 8 and abbove."""
	name = "screenCurtain"
	# Translators: Description of a vision enhancement provider that disables output to the screen,
	# making it black.
	description = _("Screen Curtain")
	supportedTransformations = (
		ColorTransformation("black", pgettext('color hue','black'), TRANSFORM_BLACK),
		# Translators: The state when the screen curtain is disabled.
		ColorTransformation("default", _("disabled"), TRANSFORM_DEFAULT)
	)
	conflictingRoles = frozenset([ROLE_MAGNIFIER, ROLE_HIGHLIGHTER])

	def __init__(self, *roles):
		winMagnification.Initialize()
		super(WinMagnificationScreenCurtain, self).__init__(*roles)

	def initializeColorEnhancer(self):
		super(WinMagnificationScreenCurtain, self).initializeColorEnhancer()
		self.transformation = self.supportedTransformations[0]

	def _get_transformation(self):
		return self._transformation

	def _set_transformation(self, transformation):
		winMagnification.SetFullscreenColorEffect(byref(transformation.value))
		self._transformation = transformation

	def terminateColorEnhancer(self):
		self.transformation = self.supportedTransformations[1]
		super(WinMagnificationScreenCurtain, self).terminateColorEnhancer()

	def terminate(self, *roles):
		winMagnification.Uninitialize()
		super(WinMagnificationScreenCurtain, self).terminate(*roles)
