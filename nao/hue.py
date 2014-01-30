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

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Provides, Requires, \
    Instantiate
import pelix.services

# Standard library
import logging

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

COLOR_MAP = {'red': 101,
             'green': 102,
             'yellow': 103,
             'blue': 104,

             # French translation
             'rouge': 101,
             'vert': 102,
             'jaune': 103,
             'bleu': 104
             }
"""
OpenHAB MQTT color map
"""

DEFAULT_COLOR = COLOR_MAP['blue']
""" Default color: blue """

#-------------------------------------------------------------------------------

@ComponentFactory('hue-control-mqtt')
@Provides('nao.hue')
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
