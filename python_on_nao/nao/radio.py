#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
MQTT Radio message sender
"""

# Nao Internals
import internals.constants

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Provides, Requires, \
    Instantiate, Validate, Invalidate
import pelix.services

# Standard library
import logging

# ------------------------------------------------------------------------------

# Module version
__version_info__ = (0, 1, 1)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

_logger = logging.getLogger(__name__)

RADIO_MAP = {'off': 0,
             'radio': 1,
             'change': 2,
             }
"""
OpenHAB MQTT radio map
"""

DEFAULT_RADIO = RADIO_MAP['radio']
""" Default radio: radio (first radio channel found) """

# ------------------------------------------------------------------------------


@ComponentFactory('radio-control-mqtt')
@Provides('nao.radio')
@Requires('_speech', internals.constants.SERVICE_SPEECH)
@Requires('_mqtt', pelix.services.SERVICE_MQTT_CONNECTOR_FACTORY)
@Requires('_behaviour', 'nao.behaviour')
@Instantiate('radio-control-mqtt')
class RadioMqttControll(object):
    """
    Controls the radio on OpenHAB
    """
    def __init__(self):
        """
        Sets up members
        """
        # Injected service
        self._mqtt = None
        self._speech = None
        self._behaviour = None

    def handle_order(self, order):
        """
        Changes the radio station or stops the radio

        :param order: The order to send to OpenHAB (off, radio or change)
        """
        # Get the order
        _logger.info("radio word=%s", order)
        value = RADIO_MAP.get(order, DEFAULT_RADIO)
        if value:
            self._behaviour.launch_behaviour('This_2')
        # else:
        #    self._behaviour.stop_behaviour('dance_twist')
        #    self._behaviour.launch_behaviour('Neutral')

        # Send the order using MQTT
        self._mqtt.publish("/nao/openhab/radio", str(value))

    def word_recognized(self, word, all_words):
        """
        A word has been recognized

        :param word: The best-match word
        :param all_words: All the words that have been recognized
        """
        # TODO: Add a threshold to handle the word only if possible
        self.handle_order(word)

    @Validate
    def _validate(self, context):
        """
        Component validated
        """
        # Register to some words
        self._speech.add_listener(self, list(RADIO_MAP.keys()))

    @Invalidate
    def _invalidate(self, context):
        """
        Component invalidated
        """
        # Unregister from speech recognition
        self._speech.remove_listener(self)
