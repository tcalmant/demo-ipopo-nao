#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Nao LEDs color changer
"""

# Module version
__version_info__ = (0, 1, 0)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

#-------------------------------------------------------------------------------

# Nao Internals
import internals.constants

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Provides, Requires, \
    Instantiate, Validate, Invalidate

# Standard library
import logging

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

COLOR_MAP = {'red': 0x00FF0000,
             'green': 0x00009900,
             'yellow': 0x00000099,
             'blue': 0x00FFFF00,

             # French translation
             'rouge': 0x00FF0000,
             'vert': 0x00009900,
             'jaune': 0x00000099,
             'bleu': 0x00FFFF00
             }
"""
Handled colors
"""

DEFAULT_COLOR = 0x00FFFFFF
""" Default color: white """

#-------------------------------------------------------------------------------

@ComponentFactory('leds-speech-control')
@Provides('nao.leds')
@Requires('_speech', internals.constants.SERVICE_SPEECH)
@Instantiate('leds-speech-control')
class LedsSpeechControll(object):
    """
    Controls the color of the LEDs on the robot
    """
    def __init__(self):
        """
        Sets up members
        """
        # Injected service
        self._speech = None

        # LEDs proxy
        self._leds = None


    def change_led(self, color):
        """
        Changes the color of the LEDs on the robot

        :param color: name of the color
        """
        # Change color. Transition lasts 1 second
        self._leds.fadeRGB('AllLeds', COLOR_MAP.get(color, DEFAULT_COLOR), 1.0)


    def word_recognized(self, filtered_words, all_words):
        """
        A word has been recognized

        :param filtered_words: The recognized words we're looking for
        :param all_words: All the words that have been recognized
        """
        # TODO: Add a threshold to handle the word only if possible
        self.change_led(filtered_words[0])


    @Validate
    def _validate(self, context):
        """
        Component validated
        """
        # Register to some words
        self._speech.add_listener(self, list(COLOR_MAP.keys()))


    @Invalidate
    def _invalidate(self, context):
        """
        Component invalidated
        """
        # Unregister from speech recognition
        self._speech.remove_listener(self)
