#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Nao LEDs color changer
"""

# Nao SDK
from naoqi import ALProxy

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Provides, Instantiate, \
    Validate, Invalidate

# Standard library
import logging

# ------------------------------------------------------------------------------

# Module version
__version_info__ = (0, 1, 1)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

_logger = logging.getLogger(__name__)

COLOR_MAP = {'red': 0x00FF0000,
             'green': 0x00009900,
             'yellow': 0x00FFFF00,
             'blue': 0x00000099,

             # French translation
             'rouge': 0x00FF0000,
             'vert': 0x00009900,
             'jaune': 0x00FFFF00,
             'bleu': 0x00000099,
             }
"""
Handled colors
"""

DEFAULT_COLOR = 0x00FFFFFF
""" Default color: white """

# ------------------------------------------------------------------------------


@ComponentFactory('leds-control')
@Provides('nao.leds')
@Instantiate('leds-control')
class LedsControl(object):
    """
    Controls the color of the LEDs on the robot
    """
    def __init__(self):
        """
        Sets up members
        """
        # LEDs proxy
        self._leds = None

    def change_leds(self, color):
        """
        Changes the color of the LEDs on the robot

        :param color: name of the color
        """
        # Change color. Transition lasts 1 second
        self._leds.fadeRGB('AllLeds', COLOR_MAP.get(color, DEFAULT_COLOR), 1.0)

    @Validate
    def _validate(self, context):
        """
        Component validated
        """
        # Prepare the LED proxy
        self._leds = ALProxy('ALLeds')

    @Invalidate
    def _invalidate(self, context):
        """
        Component invalidated
        """
        # Clean up
        self._leds = None
