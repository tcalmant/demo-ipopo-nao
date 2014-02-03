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

# Standard library
import logging
import threading

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

class NaoTTS(object):
    """
    Nao text-to-speech service
    """
    def __init__(self, nao_ip="nao.local", nao_port=9559):
        """
        Sets up members
        """
        # Set up the TTS proxy
        self._tts = ALProxy("ALTextToSpeech", nao_ip, nao_port)

        # Authorization to speak
        self._can_speak = threading.Event()
        self._can_speak.set()
        self.__speaking_lock = threading.Lock()


    def clear(self):
        """
        Clean up service usage
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

#-------------------------------------------------------------------------------

class BundleActivator(object):
    """

    Bundle activator, for Pelix
    """
    def __init__(self):
        """
        Sets up members
        """
        # Service registration
        self.__reg = None

        # TTS service
        self.__svc = None


    def start(self, context):
        """
        Registers the TTS service
        """
        # Prepare the service
        self.__svc = NaoTTS()

        # Register it
        self.__reg = context.register_service(constants.SERVICE_TTS,
                                              self.__svc, {})


    def stop(self, context):
        """
        Bundle stopped: unregister the service
        """
        # Unregister the service
        self.__reg.unregister()
        self.__reg = None

        # Clean it up
        self.__svc.clear()
        self.__svc = None

# Declare the Pelix activator
activator = BundleActivator()
