#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
MQTT Hue message sender
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
import pelix.services

# Standard library
import logging

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

COLOR_MAP = {'red': 1,
             'green': 2,
             'yellow': 3,
             'blue': 4,

             # French translation
             'rouge': 1,
             'vert': 2,
             'jaune': 3,
             'bleu': 4
             }
"""
OpenHAB MQTT color map
"""

DEFAULT_COLOR = COLOR_MAP['blue']
""" Default color: blue """

#-------------------------------------------------------------------------------

@ComponentFactory('hue-control-mqtt')
@Provides('nao.hue')
@Requires('_speech', internals.constants.SERVICE_SPEECH)
@Requires('_mqtt', pelix.services.SERVICE_MQTT_CONNECTOR_FACTORY)
@Instantiate('hue-control-mqtt')
class HueMqttControll(object):
    """
    Provides a shell command to publish messages
    """
    def __init__(self):
        """
        Sets up members
        """
        # Injected service
        self._mqtt = None
        self._speech = None


    def _make_topic(self, lamp, action):
        """
        Prepares the MQTT topic for the given action

        :param lamp: Hue lamp ID (1,2,3)
        :param action: Action on the lamp (color, percent)
        """
        return "/nao/openhab/hue{0}/{1}".format(lamp, action)


    def color(self, lamp, color):
        """
        Change color of hue

        :param lamp: Lamp ID
        :param color: String color (blue, bleu, ...)
        """
        color_value = COLOR_MAP.get(color.lower(), DEFAULT_COLOR)
        self._mqtt.publish(self._make_topic(lamp, "color"), str(color_value))


    def percent(self, lamp, value):
        """
        Changes the color percentage

        :param lamp: Lamp ID
        :param value: Power percentage (int)
        """
        if value < 0:
            value = 0
        elif value > 100:
            value = 100

        self._mqtt.publish(self._make_topic(lamp, "percent"), str(value))


    def word_recognized(self, filtered_words, all_words):
        """
        A word has been recognized

        :param filtered_words: The recognized words we're looking for
        :param all_words: All the words that have been recognized
        """
        # TODO: Add a threshold to handle the word only if possible
        self.color(1, filtered_words[0])


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
