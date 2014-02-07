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

# Nao API
from naoqi import ALProxy, ALModule

# Local module
import internals.constants as constants

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Property, Instantiate, \
    Provides, Validate, Invalidate

# Standard library
import logging

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

@ComponentFactory('nao-speech')
@Provides(constants.SERVICE_SPEECH)
@Property('_name', 'module.name', __name__.replace('.', '_'))
@Instantiate('nao-speech')
class NaoSpeechRecognition(ALModule):
    """
    Nao speech recognition service
    """
    def __init__(self, name):
        """
        Sets up members

        :param name: ALModule name
        """
        # Store the name
        self._name = name

        # Initialize the module
        ALModule.__init__(self, self._name)

        # Listeners listener -> [words]
        self._listeners = {}

        self._memory = None
        self._recog = None


    @Validate
    def _validate(self, context):
        constants.register_almodule(self._name, self)

        # Initialize the module
        ALModule.__init__(self, self._name)

        # Get the "memory" proxy, to register to callbacks
        self._memory = ALProxy("ALMemory")

        # Create the proxy
        self._recog = ALProxy("ALSpeechRecognition")
        self._recog.setLanguage("French")


    @Invalidate
    def _invalidate(self, context):
        constants.unregister_almodule(self._name)
        self._memory = None


    def clear(self):
        """
        Clean all up
        """
        # Clear vocabulary
        self._listeners.clear()

        # Unsubscribe
        self.__unsubscribe()

        # Clear references
        self._memory = None
        self._recog = None


    def __unsubscribe(self):
        """
        Unsubscribe from events
        """
        try:
            self._memory.unsubscribeToEvent("WordRecognized", self._name)

        except:
            # Ignore errors
            _logger.debug("Error unsubscribing speech recognition")


    def add_listener(self, listener, words):
        """
        Adds a speech listener

        :param listener: Listener to add
        :param words: Words recognized by the listener
        """
        self._listeners[listener] = words


    def remove_listener(self, listener):
        """
        Removes a speech listener

        :param listener: Listener to remove
        :raise KeyError: Unknown listener
        """
        del self._listeners[listener]


    def recognize(self, call_back):
        """
        Starts the recognition
        """
        # Start the speech recognition
        self._recog.setVocabulary(list(set(self._listeners.values())), True)

        # Subscribe the word recognition event
        self._memory.subscribeToEvent("WordRecognized",
                                      self._name,
                                      "on_word_recognized")


    def on_word_recognized(self, *args):
        """
        A word has been recognized
        """
        # Get what has been heard
        raw_words = self._memory.getData("WordRecognized")

        # Stop recognizing speech
        self.__unsubscribe()

        # Call listeners
        for listener, listener_words in self._listeners.items():
            # Compute recognized words
            sub_words = [word for word in raw_words if word in listener_words]

            try:
                # Call the listener
                listener.word_recognized(sub_words, raw_words[:])

            except Exception as ex:
                # Something went wrong
                _logger.exception("Error calling word listener: %s", ex)
