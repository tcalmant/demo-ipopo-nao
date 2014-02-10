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
    Instantiate
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
@Provides(pelix.services.SERVICE_EVENT_HANDLER)
@Requires('_tts', constants.SERVICE_TTS, optional=True)
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
        self._tts = None


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


    def handle_event(self, topic, properties):
        """
        An EventAdmin event has been received

        :param topic: Event topic
        :param properties: Event properties
        """
        # Check the button
        button = properties['name']
        if button == 'front':
            lamp = 1

        elif button == 'rear':
            lamp = 2

        else:
            return

        if self._tts is not None:
            # Tell the user we're ready
            self._tts.say('Je suis prêt à changer de couleur')

        # Recognize the color
        word = self._speech.single_recognize(list(COLOR_MAP.keys()))

        # Change the color
        self.color(lamp, word)

