#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Handles buttons on Nao and converts them into events
"""

# Utilities
import internals.constants as constants

# Nao API
from naoqi import ALProxy, ALModule

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Property, Requires, \
    Instantiate, Validate, Invalidate
import pelix.services

# Standard library
import logging

# ------------------------------------------------------------------------------

# Module version
__version_info__ = (0, 1, 0)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

_logger = logging.getLogger(__name__)

TOUCH_event_MAP = {  # Head
                    'FrontTactilTouched': 'front',
                    'MiddleTactilTouched': 'middle',
                    'RearTactilTouched': 'rear',
                    # Chest
                    'ChestButtonPressed': 'chest'}
"""
Touch events, sharing the same callback signature

See: https://community.aldebaran-robotics.com/doc/1-14/naoqi/sensors/
     alsensors-api.html#event-list
"""

# ------------------------------------------------------------------------------


@ComponentFactory('nao-touch')
@Requires('_event', pelix.services.SERVICE_EVENT_ADMIN)
@Property('_name', 'module.name', __name__.replace('.', '_'))
@Instantiate('nao-touch')
class NaoTouch(ALModule):
    """
    Nao speech recognition service
    """
    def __init__(self):
        """
        Sets up members
        """
        # Injected service
        self._event = None

        # Name property
        self._name = None

        # Proxy to Nao's memory
        self._memory = None

    @Validate
    def _validate(self, context):
        """
        Component validated
        """
        # Register the global in the main script
        constants.register_almodule(self._name, self)

        # Initialize the module
        ALModule.__init__(self, self._name)

        # Get the "memory" proxy, to register to callbacks
        self._memory = ALProxy("ALMemory")

        # Register to button events
        for event in TOUCH_event_MAP:
            self._memory.subscribeToEvent(event, self._name,
                                          self.on_touch_sensed.__name__)

    @Invalidate
    def _invalidate(self, context):
        """
        Component invalidated
        """
        # Unregister from button events
        for event in TOUCH_event_MAP:
            self._memory.unsubscribeToEvent(event, self._name)

        # Unregister the global
        constants.unregister_almodule(self._name)

        # Clean up
        self._memory = None

    def on_touch_sensed(self, event, value, identifier):
        """
        A touch button has been... touched

        :param event: Name of the event
        :param value: 1.0 if the button is pressed, 0.0 if it is released
        :param identifier: Name of our module
        """
        _logger.debug("Touch sensed: %s - %s", event, value)

        try:
            # Get the local name
            event_name = TOUCH_event_MAP[event]
        except KeyError:
            # Unknown name, ignore
            return

        if value:
            # On press
            event_type = "touch"
        else:
            # On release
            event_type = "release"

        # Send the event
        self._event.send('/nao/touch/{0}/{1}'.format(event_name, event_type),
                         {'event': event, 'value': value,
                          'name': event_name, 'type': event_type})
