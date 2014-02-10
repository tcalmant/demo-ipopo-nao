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

# Internals
import internals.constants

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Provides, Requires, \
    Instantiate
import pelix.shell

# Standard library
import logging

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

@ComponentFactory('nao-shell-speech')
@Provides(pelix.shell.SHELL_COMMAND_SPEC)
@Requires('_speech', internals.constants.SERVICE_SPEECH)
@Instantiate('nao-shell-speech')
class TellerShell(object):
    """
    Provides a shell command to publish messages
    """
    def __init__(self):
        """
        Sets up members
        """
        # Injected service
        self._speech = None


    def get_namespace(self):
        """
        Called by the shell service: returns the namespace of this component
        """
        return "nao"


    def get_methods(self):
        """
        Called by the shell service: returns the list of shell commands
        """
        return [('speech', self.speech_recognition)]


    def speech_recognition(self, io_handler, *args):
        """
        Speech recognition, with the given word list as vocabulary
        """
        io_handler.write_line(self._speech.simple_recognize(args))
