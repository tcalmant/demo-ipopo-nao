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
    Provides, Requires, Validate, Invalidate
import pelix.services

# Standard library
import logging
import threading

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

@ComponentFactory('nao-speech')
@Provides(constants.SERVICE_SPEECH)
@Provides(pelix.services.SERVICE_EVENT_HANDLER)
@Requires('_tts', constants.SERVICE_TTS, optional=True)
@Property('_name', 'module.name', __name__.replace('.', '_'))
@Property('_events_topics', pelix.services.PROP_EVENT_TOPICS, ['/nao/touch/*'])
@Instantiate('nao-speech')
class NaoSpeechRecognition(ALModule):
    """
    Nao speech recognition service
    """
    def __init__(self):
        """
        Sets up members
        """
        # Component properties
        self._name = None
        self._events_topics = None

        # Injected TTS
        self._tts = None

        # Listeners listener -> [words]
        self._listeners = {}

        # ALProxies
        self._memory = None
        self._recog = None

        # Flags
        self.__lock = threading.RLock()
        self._can_recog = threading.Event()
        self._single_recognized = threading.Event()


    @Validate
    def _validate(self, context):
        """
        Component validated
        """
        _logger.debug("Validating speech...")

        # Register the module as a global in __main__
        constants.register_almodule(self._name, self)

        # Initialize the module
        ALModule.__init__(self, self._name)

        # Get the "memory" proxy, to register to callbacks
        self._memory = ALProxy("ALMemory")

        # Just to be sure...
        try:
            self._memory.unsubscribeToEvent("WordRecognized", self._name)
        except:
            _logger.debug("Speech wasn't yet registered")

        # Create the proxy
        self._recog = ALProxy("ALSpeechRecognition")
        self._recog.setLanguage("French")

        # We're ready
        self._can_recog.set()

        _logger.debug("Speech ready")


    @Invalidate
    def _invalidate(self, context):
        """
        Component invalidated
        """
        # Clear vocabulary
        self._listeners.clear()

        # Unsubscribe from the speech recognition
        self.__unsubscribe()

        # Unregister the module
        constants.unregister_almodule(self._name)

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

        finally:
            # In any case, resume the TTS service
            if self._tts is not None:
                self._tts.resume()

            # Authorize again
            self._can_recog.set()


    def handle_event(self, topic, properties):
        """
        An EventAdmin event has been received

        :param topic: Event topic
        :param properties: Event properties
        """
        if not self._can_recog.is_set():
            # Already recognizing
            _logger.debug('Already recognizing')
            return

        with self.__lock:
            button = properties['name']
            if button not in ('front', 'middle'):
                # Only handle head front and middle buttons
                return

            pressed = bool(properties['value'])
            if pressed:
                # Button pressed/touched: start recognition
                if self._tts is not None:
                    # Tell the user we're ready
                    self._tts.say('Je vous écoute')

                # Start recognition
                self.recognize()


    def add_listener(self, listener, words):
        """
        Adds a speech listener

        :param listener: Listener to add
        :param words: Words recognized by the listener
        """
        self._listeners[listener] = words
        _logger.info("Adding words: %s (%s)", words, type(words).__name__)


    def remove_listener(self, listener):
        """
        Removes a speech listener

        :param listener: Listener to remove
        :raise KeyError: Unknown listener
        """
        del self._listeners[listener]


    def recognize(self, words=None):
        """
        Starts the recognition

        :param words: The vocabulary to use (optional)
        """
        self._can_recog.clear()

        # Start the speech recognition
        if not words:
            words = set()
            for listener_words in self._listeners.values():
                words.update(listener_words)

        self._recog.setVocabulary(list(words), True)

        # Pause the TTS service, if any
        if self._tts is not None:
            self._tts.pause()

        # Subscribe the word recognition event
        self._memory.subscribeToEvent("WordRecognized",
                                      self._name,
                                      self.on_word_recognized.__name__)


    def simple_recognize(self, words):
        """
        One-shot recognition
        """
        # Wait to be able to recognize
        self._can_recog.wait()
        self._can_recog.clear()

        # Prepare the recognition
        self._recog.setVocabulary(list(words), True)
        self._single_recognized.clear()

        # Pause the TTS service, if any
        if self._tts is not None:
            self._tts.pause()

        # Subscribe the word recognition event
        self._memory.subscribeToEvent("WordRecognized",
                                      self._name,
                                      self.on_single_recognized.__name__)

        # Wait for the word to be recognized
        self._single_recognized.wait()

        # Store the word
        result = self._single_result

        # Return the found word
        return result


    def on_single_recognized(self, event, raw_words, identifier):
        """
        A word has been recognized
        """
        # Set up the "single" result
        self._single_result = raw_words[0]
        self._single_recognized.set()

        # Prepare next run
        self.__unsubscribe()


    def on_word_recognized(self, event, raw_words, identifier):
        """
        A word has been recognized
        """
        # Stop recognizing speech
        self.__unsubscribe()

        _logger.debug("Recognized: %s", raw_words)

        # Get the first recognized word
        word = raw_words[0]
        _logger.debug("Using word: %s", word)

        # Call listeners
        for listener, listener_words in self._listeners.items():
            # Compute recognized words
            if word in listener_words:
                # Notify the listener only if it is one of its words that
                # have been heard
                try:
                    # Call the listener
                    listener.word_recognized(word, raw_words[:])

                except Exception as ex:
                    # Something went wrong
                    _logger.exception("Error calling word listener: %s", ex)
