#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Nao text-to-speech service
"""

# Module version
__version_info__ = (0, 1, 0)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

#-------------------------------------------------------------------------------

# Nao API
from naoqi import ALProxy

# Local module
import internals.constants as constants

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Instantiate, Provides, \
    Validate, Invalidate

# Standard library
import logging
import threading

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

@ComponentFactory('nao-tts')
@Provides(constants.SERVICE_TTS)
@Instantiate('nao-tts')
class NaoTTS(object):
    """
    Nao text-to-speech service
    """
    def __init__(self):
        """
        Sets up members
        """
        self._tts = None

        # Authorization to speak
        self._can_speak = threading.Event()
        self._can_speak.set()
        self.__speaking_lock = threading.Lock()


    @Validate
    def validate(self, context):
        """
        Component validated
        """
        # Set up the TTS proxy
        self._tts = ALProxy("ALTextToSpeech")


    @Invalidate
    def invalidate(self, context):
        """
        Component invalidated
        """
        # Stop using the proxy
        self._tts = None

        # Unlock everything
        self._can_speak.set()


    def say(self, sentence):
        """
        Says the given sentence

        :param sentence: Text to say
        """
        with self.__speaking_lock:
            # Wait to be authorized to speak
            self._can_speak.wait()

            # Say what we have to
            self._tts.say(sentence)


    def resume(self):
        """
        Allows Nao to speak
        """
        self._can_speak.set()


    def pause(self):
        """
        Forbids Nao to speak
        """
        if self._can_speak.is_set():
            with self.__speaking_lock:
                self._can_speak.clear()
