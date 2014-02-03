#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
MQTT Radio message sender
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

RADIO_MAP = {'off': 0,
             'radio': 1,
             'change': 2,
             }

"""
OpenHAB MQTT radio map
"""

DEFAULT_RADIO = RADIO_MAP['radio']
""" Default Radion : radio (premiere chaine station ) """

#-------------------------------------------------------------------------------

@ComponentFactory('radio-control-mqtt')
@Provides('nao.radio')
@Requires('_mqtt', pelix.services.SERVICE_MQTT_CONNECTOR_FACTORY)
@Instantiate('radio-control-mqtt')
class RadioMqttControll(object):
    """
    Provides a shell command to publish messages
    """
    def __init__(self):
        """
        Sets up members
        """
        # Injected service
        self._mqtt = None


    def _make_topic(self):
        """
        Prepares the MQTT topic for the given action
                
        :param station_number: Action on the radio: number of the station
        """
        return "/nao/openhab/radio"

    def station(self, station_number):
        """
        Changes the radio station
 
        :param value: station number where 0 = off
        """
        value = RADIO_MAP.get(station_number.lower(), DEFAULT_RADIO)
        self._mqtt.publish(self._make_topic(), str(value))