#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Starts the Pelix framework and the Nao internals services
"""

#-------------------------------------------------------------------------------

# Standard library
from optparse import OptionParser
import logging
import sys

# Nao SDK
from naoqi import ALBroker

# Update the Python path
sys.path.insert(0, "/home/nao/python-libs")

# Pelix
from pelix.framework import create_framework
from pelix.ipopo.constants import use_ipopo
import pelix.services

#-------------------------------------------------------------------------------

# Nao IP address
NAO_IP = "nao.local"

_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

def main(pip, pport):
    """
    Main entry point
    """
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",  # listen to anyone
       0,  # find a free port and use it
       pip,  # parent broker IP
       pport)  # parent broker port

    # Create the Pelix framework
    framework = create_framework((# iPOPO
                                  'pelix.ipopo.core',

                                  # Shell bundles
                                  'pelix.shell.core',
                                  'pelix.shell.console',
                                  'pelix.shell.remote',
                                  'pelix.shell.ipopo',

                                  # ConfigurationAdmin
                                  'pelix.services.configadmin',
                                  'pelix.shell.configadmin',

                                  # EventAdmin,
                                  'pelix.services.eventadmin',
                                  'pelix.shell.eventadmin',

                                  # MQTT
                                  'pelix.services.mqtt',

                                  # Nao Internals
                                  'internals.speech',
                                  'internals.touch',
                                  'internals.tts',

                                  # Nao Demo
                                  'nao.shell',
                                  'nao.behaviour',
                                  'nao.hue',
                                  'nao.leds',
                                  'nao.radio',
                                  'nao.teller'))

    # Start the framework
    framework.start()

    # Instantiate EventAdmin
    with use_ipopo(framework.get_bundle_context()) as ipopo:
        ipopo.instantiate(pelix.services.FACTORY_EVENT_ADMIN, 'event-admin', {})

    try:
        # Wait for the framework to stop
        framework.wait_for_stop()

    except KeyboardInterrupt:
        print("Interrupted by user, shutting down")
        framework.stop()
        myBroker.shutdown()
        sys.exit(0)

#-------------------------------------------------------------------------------

if __name__ == "__main__":
    # Setup logs
    logging.basicConfig(level=logging.INFO)

    # Parse arguments
    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=NAO_IP,
        pport=9559)

    (opts, args_) = parser.parse_args()
    pip = opts.pip
    pport = opts.pport

    # Run the script
    main(pip, pport)
