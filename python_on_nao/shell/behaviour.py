#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
MQTT Hue message sender
"""

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Provides, Requires, \
    Instantiate
import pelix.shell

# Standard library
import logging

# ------------------------------------------------------------------------------

# Module version
__version_info__ = (0, 1, 0)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

_logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------


@ComponentFactory('nao-shell-behaviour')
@Provides(pelix.shell.SHELL_COMMAND_SPEC)
@Requires('_behaviour', 'nao.behaviour')
@Instantiate('nao-shell-behaviour')
class NaoShell(object):
    """
    Provides a shell command to publish messages
    """
    def __init__(self):
        """
        Sets up members
        """
        # Injected service
        self._behaviour = None

    def get_namespace(self):
        """
        Called by the shell service: returns the namespace of this component
        """
        return "nao"

    def get_methods(self):
        """
        Called by the shell service: returns the list of shell commands
        """
        return [('list_behaviours', self.list_behaviours),
                ('running_behaviours', self.list_behaviours),
                ('play', self.play_behaviour)]

    def list_behaviours(self, io_handler):
        """
        Prints known behaviours
        """
        known = self._behaviour.get_behaviours()[0]
        io_handler.write_line('Known behaviours:')
        for name in known:
            io_handler.write_line('\t- {0}', name)

    def running_behaviours(self, io_handler):
        """
        Prints running behaviours
        """
        running = self._behaviour.get_behaviours()[1]
        io_handler.write_line('Running behaviours:')
        for name in running:
            io_handler.write_line('\t- {0}', name)

    def play_behaviour(self, io_handler, behaviour):
        """
        Plays a behaviour
        """
        self._behaviour.launch_behaviour(behaviour)
