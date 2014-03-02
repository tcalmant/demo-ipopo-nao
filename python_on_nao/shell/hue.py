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

@ComponentFactory('nao-shell-hue')
@Provides(pelix.shell.SHELL_COMMAND_SPEC)
@Requires('_hue', 'nao.hue')
@Instantiate('nao-shell-hue')
class NaoShell(object):
    """
    Provides a shell command to publish messages
    """
    def __init__(self):
        """
        Sets up members
        """
        # Injected service
        self._hue = None


    def get_namespace(self):
        """
        Called by the shell service: returns the namespace of this component
        """
        return "nao"


    def get_methods(self):
        """
        Called by the shell service: returns the list of shell commands
        """
        return [('hue_color', self.lamp_color),
                ('hue_percent', self.lamp_percent)]


    def lamp_color(self, io_handler, lamp, color):
        """
        Change color of Philips Lamp
        """
        self._hue.color(lamp, color)


    def lamp_percent(self, io_handler, lamp, value):
        """
        Change the power of Philips Lamp (value: integer percentage)
        """
        try:
            value = int(value)

        except ValueError:
            _logger.warning("Invalid value: %s", value)

        else:
            self._hue.percent(lamp, value)
