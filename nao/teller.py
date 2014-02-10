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

# Nao Internals
import internals.constants

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Provides, Property, \
    Instantiate, Requires, Validate, Invalidate
import pelix.services as services

# Standard library
import logging

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

@ComponentFactory('nao-teller')
@Requires('_speech', internals.constants.SERVICE_SPEECH)
@Requires('_tts', internals.constants.SERVICE_TTS)
@Provides('nao.teller')
@Provides(services.SERVICE_MQTT_LISTENER)
@Property('_topics', services.PROP_MQTT_TOPICS, '/openhab/nao/+')
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

        # Nao services
        self._speech = None
        self._tts = None

        # Setup the map of orders
        self.__orders = {'porte': self.say_door}

        for name in ('meteo', 'météo'):
            self.__orders[name] = self.say_weather

        for name in ('température', 'intérieur'):
            self.__orders[name] = self.say_temperature

        # Last known states
        self._door_state = None
        self._last_temperature = None
        self._last_weather = None


    def handle_mqtt_message(self, topic, payload, qos):
        """
        An MQTT message has been received
        """
        # Topics: /openhab/nao/[door,temperature,weather]
        item = topic.split('/')[3]

        # Store state
        if item == "door":
            self._door_state = payload

        elif item == "temperature":
            # Replace '.' by ',' in numbers (better TTS results)
            self._last_temperature = payload.replace('.', ',')

        elif item == "weather":
            # Replace '.' by ',' in numbers (better TTS results)
            self._last_weather = payload.replace('.', ',')


    def say(self, sentence):
        """
        Says something
        """
        self._tts.say(sentence)


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

        self._tts.say("La porte est {0}".format(state))


    def say_temperature(self):
        """
        Says the last known interior temperature
        """
        payload = self._last_temperature
        if payload is None:
            sentence = "Je n'ai pas d'information sur la température " \
                       "intérieure."
        else:
            sentence = "La température intérieure est de {0} degrés celsius" \
                       .format(payload)

        self._tts.say(sentence)


    def say_weather(self):
        """
        Says the last known exterior temperature
        """
        payload = self._last_weather

        if payload is None:
            sentence = "Je n'ai pas d'information sur la température " \
                       "extérieure."
        else:
            sentence = "La température extérieure est de {0} degrés celsius" \
                        .format(payload)

        self._tts.say(sentence)


    def word_recognized(self, word, all_words):
        """
        A word has been recognized

        :param word: The best-match word
        :param all_words: All the words that have been recognized
        """
        # Execute the order
        self.__orders[word]()


    @Validate
    def _validate(self, context):
        """
        Component validated
        """
        # Register to some words
        self._speech.add_listener(self, list(self.__orders.keys()))


    @Invalidate
    def _invalidate(self, context):
        """
        Component invalidated
        """
        # Unregister from speech recognition
        self._speech.remove_listener(self)
