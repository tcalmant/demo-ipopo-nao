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
import pelix.shell

# Standard library
import logging

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

@ComponentFactory('nao-shell-teller')
@Provides(pelix.shell.SHELL_COMMAND_SPEC)
@Requires('_teller', 'nao.teller')
@Instantiate('nao-shell-teller')
class TellerShell(object):
    """
    Provides a shell command to publish messages
    """
    def __init__(self):
        """
        Sets up members
        """
        # Injected service
        self._teller = None


    def get_namespace(self):
        """
        Called by the shell service: returns the namespace of this component
        """
        return "nao"


    def get_methods(self):
        """
        Called by the shell service: returns the list of shell commands
        """
        return [('say', self.say),
                ('say_temperature', self.say_temperature),
                ('say_weather', self.say_weather),
                ('say_door', self.say_door)]


    def say(self, io_handler, *words):
        """
        Says something
        """
        self._teller.say(' '.join(words))

    def say_door(self, io_handler):
        """
        Says the last known value of the door
        """
        self._teller.say_door()


    def say_temperature(self, io_handler):
        """
        Says the last known value of the interior temperature
        """
        self._teller.say_temperature()


    def say_weather(self, io_handler):
        """
        Says the last known value of the exterior temperature
        """
        self._teller.say_weather()
