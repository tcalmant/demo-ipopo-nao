#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Handles buttons on Nao
"""

# Module version
__version_info__ = (0, 1, 0)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

#-------------------------------------------------------------------------------

# Utilities
import internals.constants as constants

# Nao API
from naoqi import ALProxy, ALModule

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Provides, Requires, \
    Instantiate, Validate, Invalidate, Property

# Standard library
import logging
import sys

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

@ComponentFactory('nao-touch')
@Requires('_tts', constants.SERVICE_TTS)
@Property('_name', 'module.name', __name__.replace('.', '_'))
@Instantiate('nao-touch')
class NaoTouch(ALModule):
    """
    Nao speech recognition service
    """
    def __init__(self):
        """
        Sets up members

        :param name: ALModule name
        """
        # Members
        self._tts = None
        self._name = None
        self._memory = None


    @Validate
    def _validate(self, context):
        constants.register_almodule(self._name, self)

        # Initialize the module
        ALModule.__init__(self, self._name)

        # Get the "memory" proxy, to register to callbacks
        self._memory = ALProxy("ALMemory")

        # Register to events
        self._memory.subscribeToEvent("MiddleTactilTouched",
                                      self._name,
                                      "onMiddleTouchSensed")
        self._memory.subscribeToEvent("FrontTactilTouched",
                                      self._name,
                                      "onFrontTouchSensed")


    @Invalidate
    def _invalidate(self, context):
        self._memory.unsubscribeToEvent("MiddleTactilTouched", self._name)
        self._memory.unsubscribeToEvent("FrontTactilTouched", self._name)

        constants.unregister_almodule(self._name)

        self._memory = None


    def onMiddleTouchSensed(self, event, value, *args):
        """
        Middle touch button sensed
        """
        if not value:
            # On release
            _logger.info("Got middle touch")


    def onFrontTouchSensed(self, event, value, *args):
        if not value:
            # On release
            _logger.info("Got front touch")
