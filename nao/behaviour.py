#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Nao movements
"""

# Module version
__version_info__ = (0, 1, 0)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

#-------------------------------------------------------------------------------

# Nao Internals
import internals.constants

# Nao SDK
from naoqi import ALProxy

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Provides, Requires, \
    Instantiate, Validate, Invalidate

# Standard library
import logging
import time

#-------------------------------------------------------------------------------

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

BEHAVIOURS_MAP = {'danse': 'dance_twist',
                  'droite': 'show_right',
                  'gauche': 'show_left',
                  'bonjour': 'Hello',
                  'hello': 'Hello',
                  'merci': 'Salute_1',
                  'navette': 'SpaceShuttle',
                  'applaudi': 'Applause_1',
                  'étire': 'strech1',
                  'bravo': 'winner'}
"""
Order -> Behaviour name association
"""

DEFAULT_BEHAVIOUR = "Neutral"
""" Default behaviour """

#-------------------------------------------------------------------------------

@ComponentFactory('nao-behaviour-control')
@Provides('nao.behaviour')
@Requires('_speech', internals.constants.SERVICE_SPEECH)
@Instantiate('nao-behaviour-control')
class NaoBehaviour(object):
    """
    Provides a shell command to publish messages
    """
    def __init__(self):
        """
        Sets up members
        """
        # Injected service
        self._speech = None

        # Behaviour manager
        self._manager = None


    def get_behaviours(self):
        """
        Prints and returns the list of known and of running behaviours

        :return: A tuple (list of known behaviours, list of running ones)
        """
        return self._manager.getInstalledBehaviors(), \
            self._manager.getRunningBehaviors()


    def launch_behaviour(self, behaviour, blocking=False):
        """
        Launches the given behaviour, if possible

        :param behaviour: The name of a behaviour
        """
        # Check if the behaviour exists
        if self._manager.isBehaviorInstalled(behaviour):
            # Check if it is not already running
            if not self._manager.isBehaviorRunning(behaviour):
                # Launch behavior. This is a blocking call,
                # use post if you do not want to wait for the behavior to
                # finish.
                if not blocking:
                    self._manager.post.runBehavior(behaviour)

                else:
                    self._manager.runBehavior(behaviour)

            else:
                _logger.warning("A behaviour is already running")

        else:
            _logger.warning("Unknown behaviour: %s", behaviour)


    def stop_behaviour(self, behaviour):
        """
        Stops the given behaviour, if possible

        :param behaviour: The name of a behaviour
        """
        # Check if it is already running
        if self._manager.isBehaviorRunning(behaviour):
            # Stop it, and wait a little
            self._manager.stopBehavior(behaviour)
            time.sleep(.3)

        else:
            _logger.info("Behaviour %s is not running", behaviour)


    def word_recognized(self, word, all_words):
        """
        A word has been recognized

        :param word: The best-match word
        :param all_words: All the words that have been recognized
        """
        # TODO: Add a threshold to handle the word only if possible
        self.launch_behaviour(BEHAVIOURS_MAP.get(word, DEFAULT_BEHAVIOUR))


    @Validate
    def _validate(self, context):
        """
        Component validated
        """
        # Make the proxy to the behaviour manager
        self._manager = ALProxy("ALBehaviorManager")

        # Setup the motion control
        motion = ALProxy("ALMotion")
        motion.setStiffnesses("Body", 1.0)

        # Print available behaviours
        self.get_behaviours()

        # Go in neutral mode
        self.launch_behaviour(DEFAULT_BEHAVIOUR)

        # Register to some words
        self._speech.add_listener(self, list(BEHAVIOURS_MAP.keys()))


    @Invalidate
    def _invalidate(self, context):
        """
        Component invalidated
        """
        # Unregister from speech recognition
        self._speech.remove_listener(self)

        # Clean up
        self._manager = None
