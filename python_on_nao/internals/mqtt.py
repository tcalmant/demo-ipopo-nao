#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
MQTT communications service
"""

# MQTT client
import pelix.misc.mqtt_client as mqtt

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Provides, Requires, \
    Validate, Invalidate, Instantiate, BindField, UnbindField, UpdateField, \
    Property
from pelix.utilities import to_iterable
import pelix.constants as constants
import pelix.services as services
import pelix.threadpool

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


@ComponentFactory()
@Provides(services.SERVICE_CONFIGADMIN_MANAGED)
@Property('_pid', constants.SERVICE_PID, services.MQTT_CONNECTOR_FACTORY_PID)
@Requires('_listeners', services.SERVICE_MQTT_LISTENER,
          aggregate=True, optional=True)
@Instantiate('mqtt-connector')
class MqttConnector(object):
    """
    Handles connections to MQTT servers
    """
    def __init__(self):
        """
        Sets up members
        """
        # ConfigAdmin PID
        self._pid = None

        # Injected topic listeners
        self._listeners = []

        # Topics to subscribe to (topic -> nb_references)
        self._topics = {}

        # Bundle context
        self._context = None

        # Active connection
        self._mqtt = None

        # Notification pool
        self._pool = None

    def updated(self, properties):
        """
        Configuration updated

        :param properties: Configuration properties
        """
        if self._mqtt is not None:
            # A client is still connected: disconnect first
            self._mqtt.disconnect()
            self._mqtt = None

        if properties is None:
            # Configuration deleted. Stop here
            return

        # Extract connection properties
        host = properties['host']
        port = properties.get('port', 1883)
        keepalive = properties.get('keepalive', 60)

        # Debug
        _logger.debug("Connecting to [%s]:%s ...", host, port)

        # Setup the client
        self._mqtt = mqtt.MqttClient()
        self._mqtt.on_connect = self.__on_connect
        self._mqtt.on_message = self.__on_message
        self._mqtt.connect(host, port, keepalive)

    def publish(self, topic, payload, qos=0, retain=False):
        """
        Publishes an MQTT message if the client is connected
        """
        if self._mqtt is not None:
            self._mqtt.publish(topic, payload, qos, retain)

    @Validate
    def _validate(self, context):
        """
        Component validated
        """
        self._context = context

        # Start the notification pool
        self._pool = pelix.threadpool.ThreadPool(
            2, logname="mqtt-notifications")
        self._pool.start()
        _logger.info("MQTT connector validated")

    @Invalidate
    def _invalidate(self, context):
        """
        Component invalidated
        """
        # Stop the notification pool
        self._pool.stop()

        # Disconnect from the server
        if self._mqtt is not None:
            self._mqtt.disconnect()

        # Clean up
        self._mqtt = None
        self._pool = None
        self._context = None
        _logger.info("MQTT connector invalidated")

    @BindField('_listeners')
    def _bind_listener(self, field, listener, svc_ref):
        """
        A new MQTT listener has been bound
        """
        topics = to_iterable(
            svc_ref.get_property(services.PROP_MQTT_TOPICS), False)
        for topic in topics:
            self.__add_listener(topic, listener)

    @UpdateField('_listeners')
    def _update_listener(self, field, listener, svc_ref, old_props):
        """
        A listener has been updated
        """
        old_topics = set(old_props[services.PROP_MQTT_TOPICS])
        topics = set(
            to_iterable(
                svc_ref.get_property(services.PROP_MQTT_TOPICS), False))

        # New topics
        for topic in topics.difference(old_topics):
            self.__add_listener(topic, listener)

        # Removed old ones
        for topic in old_topics.difference(topics):
            self.__remove_listener(topic, listener)

    @UnbindField('_listeners')
    def _unbind_listener(self, field, listener, svc_ref):
        """
        An MQTT listener is gone
        """
        topics = to_iterable(
            svc_ref.get_property(services.PROP_MQTT_TOPICS), False)
        for topic in topics:
            self.__remove_listener(topic, listener)

    def __add_listener(self, topic, listener):
        """
        Adds a topic listener
        """
        try:
            # Get current listeners
            listeners = self._topics[topic]
        except KeyError:
            # New topic: subscribe to it
            listeners = self._topics[topic] = set()
            self.__subscribe(topic)

        # Store the listener
        listeners.add(listener)

    def __remove_listener(self, topic, listener):
        """
        Removes a topic listener
        """
        try:
            listeners = self._topics[topic]
            listeners.remove(listener)
            if not listeners:
                # No more reference to the topic, unsubscribe
                del self._topics[topic]
                self.__unsubscribe(topic)
        except KeyError:
            # Unused topic or listener not registered for it
            pass

    def __on_connect(self, client, result_code):
        """
        MQTT Client connected to the server
        """
        if result_code == 0:
            # Success !
            _logger.info("Connected to the MQTT server")

            # Subscribe to topics
            for topic in self._topics:
                client.subscribe(topic, 0)

    def __on_message(self, client, msg):
        """
        A message has been received from a server
        """
        try:
            # Get the topic
            topic = msg.topic

            # Get all listeners matching this topic
            all_listeners = set()
            for subscription, listeners in self._topics.items():
                if mqtt.MqttClient.topic_matches(subscription, topic):
                    all_listeners.update(listeners)

            # Notify them using the pool
            self._pool.enqueue(self.__notify_listeners, all_listeners,
                               topic, msg.payload, msg.qos)
        except KeyError:
            # No listener for this topic
            pass

    @staticmethod
    def __notify_listeners(listeners, topic, payload, qos):
        """
        Notifies listeners of an MQTT message
        """
        for listener in listeners:
            try:
                listener.handle_mqtt_message(topic, payload, qos)
            except Exception as ex:
                _logger.exception("Error calling MQTT listener: %s", ex)

    def __subscribe(self, topic):
        """
        Subscribes to a topic
        """
        if self._mqtt is not None:
            self._mqtt.subscribe(topic, 0)

    def __unsubscribe(self, topic):
        """
        Unsubscribes from a topic
        """
        if self._mqtt is not None:
            self._mqtt.unsubscribe(topic)
