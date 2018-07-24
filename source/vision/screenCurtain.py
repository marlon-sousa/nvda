#vision/screenCurtain.py
#A part of NonVisual Desktop Access (NVDA)
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
#Copyright (C) 2018 NV Access Limited

"""Screen curtain implementation based on the windows magnification API."""

from . import ColorEnhancer, ColorTransformation, ROLE_MAGNIFIER
import winMagnification
from ctypes import byref
import winVersion

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
	description = _("Screen Curtain")
	supportedTransformations = (
		ColorTransformation("black", pgettext('color hue','black'), TRANSFORM_BLACK),
		# Translators: The state when the screen curtain is disabled.
		ColorTransformation("default", _("disabled"), TRANSFORM_BLACK)
	)
	conflictingRoles = frozenset([ROLE_MAGNIFIER])

	def __init__(self, *roles):
		if (winVersion.winVersion.major, winVersion.winVersion.minor) < (6, 2):
			raise RuntimeError("This vision enhancement provider is only supported on Windows 8 and above")
		winMagnification.Initialize()
		super(ScreenCurtain, self).__init__(*roles)

	def initializeColorEnhancer(self):
		super(ScreenCurtain, self).initializeColorEnhancer()
		self.transformation = self.supportedTransformations[0]

	def _get_transformation(self):
		return self._transformation

	def _set_transformation(self, transformation):
		winMagnification.SetFullscreenColorEffect(byref(transformation.value))
		self._transformation = transformation

	def terminateColorEnhancer(self):
		self.transformation = self.supportedTransformations[1]
		super(ScreenCurtain, self).terminateColorEnhancer()

	def terminate(self, *roles):
		winMagnification.Deinitialize()
		super(ScreenCurtain, self).terminate(*roles)
