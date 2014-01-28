#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Nao speech controller
"""

# Module version
__version_info__ = (0, 1, 0)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

#-------------------------------------------------------------------------------

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Provides, Property, \
    Instantiate, Requires
import pelix.services as services

# Standard library
import logging

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

@ComponentFactory('nao-teller')
@Requires('_nao', 'nao.core')
@Provides('nao.teller')
@Provides(services.SERVICE_MQTT_LISTENER)
@Property('_topics', services.PROP_MQTT_TOPICS, '/openhab/+')
@Instantiate('nao-teller')
class NaoStateTeller(object):
    """
    A simple MQTT client
    """
    def __init__(self):
        """
        Sets up members
        """
        # Properties
        self._topics = None

        # Nao core service
        self._nao = None

        # Last known states
        self._door_state = None
        self._last_temperature = None
        self._last_weather = None


    def handle_mqtt_message(self, topic, payload, qos):
        """
        An MQTT message has been received
        """
        item = topic.split('/')[2]

        # Store state
        if item == "door":
            self._door_state = payload

        elif item == "temperature":
            self._last_temperature = payload.replace('.', ',')

        elif item == "weather":
            self._last_weather = payload.replace('.', ',')


    def say(self, sentence):
        """
        Says something
        """
        self._nao.say(sentence)


    def say_door(self):
        """
        Says the last known state of the door
        """
        payload = self._door_state
        if payload == "CLOSED":
            state = "fermée"
        elif payload == "OPEN":
            state = "ouverte"
        else:
            state = "dans un état que je ne connais pas"

        self._nao.say("La porte est {0}".format(state))


    def say_temperature(self):
        """
        Says the last known interior temperature
        """
        payload = self._last_temperature
        if payload is None:
            sentence = "Je n'ai pas d'information sur la température intérieure."
        else:
            sentence = "La température intérieure est de {0} degrés celsius" \
                       .format(payload)

        self._nao.say(sentence)


    def say_weather(self):
        """
        Says the last known exterior temperature
        """
        payload = self._last_weather

        if payload is None:
            sentence = "Je n'ai pas d'information sur la température extérieure."
        else:
            sentence = "La température extérieure est de {0} degrés celsius" \
                        .format(payload)

        self._nao.say(sentence)
