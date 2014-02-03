#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Script for Nao

@author: johal
"""

#-------------------------------------------------------------------------------

# Standard library
from optparse import OptionParser
import logging
import sys
import time

# Nao SDK
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

# Update the Python path
sys.path.insert(0, "/home/nao/python-libs")

# Pelix
from pelix.framework import create_framework
from pelix.ipopo.constants import use_ipopo

#-------------------------------------------------------------------------------

# Nao IP address
NAO_IP = "nao.local"

# Global variable to store the HumanGreeter module instance
HumanGreeter = None
memory = None
speechrecog = None
managerProxy = None
tts = None
isDoneSpeaking =True
colorwordList = ["bleu", "rouge", "vert", "jaune"]


radioList = ["radio", "change", "off"]

wordList = ["hello","porte", "température", "meteo","bye"]
behaviourList =["dance_twist", "show_right", "show_left","Hello","Applause_1", "Salute_1",'SpaceShuttle', 'mysticalpower', 'stretch1', 'stretch2', 'stretch3', 'winner']


_logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------

class NaoTouchModule(ALModule):
    """ A simple module able to touch events
    """
    def __init__(self, name):
        ALModule.__init__(self, name)

        # HUE service
        self._hue = None
        # Radio service
        self._radio = None
        self._teller = None

        # Create a proxy to ALTextToSpeech for later use
        global tts
        tts = ALProxy("ALTextToSpeech", NAO_IP, 9559)
        tts.enableNotifications()

        # Subscribe to the Touch and text to speech event:
        global memory
        self.leds = ALProxy("ALLeds", NAO_IP, 9559)
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("MiddleTactilTouched",
            "HumanGreeter",
            "onMiddleTouchSensed")
        memory.subscribeToEvent("FrontTactilTouched",
            "HumanGreeter",
            "onFrontTouchSensed")
        memory.subscribeToEvent("ALTextToSpeech/TextDone", 
            "HumanGreeter",
            "onDoneSpeaking")
        # Proxy to launch behaviour embedded on the robot
        managerProxy = ALProxy("ALBehaviorManager", NAO_IP, 9559)
        # Proxy to launch behaviour embedded on the robot
        motion = ALProxy("ALMotion", "nao.local", 9559)
        motion.setStiffnesses("Body", 1.0)
            
        speechrecog = ALProxy("ALSpeechRecognition")
        speechrecog.setLanguage("French")
        

        try:
            speechrecog.setVocabulary(wordList, True)

        except Exception as ex:
            _logger.warning("Got exception: %s", ex)

        launchBehavior(managerProxy, "Hello")
        tts.say("Je suis prêt à recevoir des ordres")

    def getBehaviors(self, managerProxy):
        ''' Know which behaviors are on the robot '''

        names = managerProxy.getInstalledBehaviors()
        print "Behaviors on the robot:"
        print names

        names = managerProxy.getRunningBehaviors()
        print "Running behaviors:"
        print names
        
    def launchBehavior(self, managerProxy, behaviorName):
        ''' Launch and stop a behavior, if possible. '''

        # Check that the behavior exists.
        if (managerProxy.isBehaviorInstalled(behaviorName)):
            # Check that it is not already running.
            if (not managerProxy.isBehaviorRunning(behaviorName)):
                # Launch behavior. This is a blocking call, use post if you do not
                # want to wait for the behavior to finish.
                managerProxy.post.runBehavior(behaviorName)
                time.sleep(0.5)
            else:
                print "Behavior is already running."
        
        else:
            print "Behavior not found."
            return
    
#       names = managerProxy.getRunningBehaviors()
#       print "Running behaviors:"
#       print names

    def stopBehavior(self, managerProxy, behaviorName):
        # Stop the behavior.
        if (managerProxy.isBehaviorRunning(behaviorName)):
            managerProxy.stopBehavior(behaviorName)
            time.sleep(1.0)
        else:
            print "Behavior is already stopped."

 
    def changeLed(self, color):
        """
        Changes the LEDs on the robot
        """
        duration = 1.0
        if color == "rouge":
            rgb = 0x00FF0000
        elif color == "vert":
            rgb = 0x00009900
        elif color == "bleu":
            rgb = 0x00000099
        elif color == "jaune":
            rgb = 0x00FFFF00
        else:
            # Default
            rgb = 0x00FFFFFF

        # Change LEDs on the Robot
        self.leds.fadeRGB('AllLeds', rgb, duration)
        

        if self._hue is not None:
            # Change lamp color
            self._hue.color(1, color)


    def changeRadio(self, station_number):
    
        if self._radio is not None:
            # Change lamp color
            self._radio.station(station_number)


    def onStateRequest(self, item):
        """
        Requests the state of an item
        """
        if item == "porte":
            self._teller.say_door()

        elif item == "température":
            self._teller.say_temperature()

        elif item == "meteo":
            self._teller.say_weather()
    
    def onDoneSpeaking(self, key, value, message):
        isDoneSpeaking=value
        pass

    def onSpeechRecognized(self, *_args):
        """
        This will be called each time a speech is detected.
        """
        # Unsubscribe to the event when talking,
        # to avoid repetitions
        launchBehaviour(managerProxy,"mentalist)
        words = memory.getData("WordRecognized");
        word = words[0]
        _logger.info("Heard %s (%s)", word, words)
        
        if word in ("porte", "meteo", "température"):
            # State order
            self.onStateRequest(word)

        else:
            # Color given
            self.changeLed(words[0])
            launchBehaviour(managerProxy,'show_right')
        time.sleep(1)

        # Subscribe again to the event
        memory.unsubscribeToEvent("WordRecognized",
            "HumanGreeter")


    def onMiddleTouchSensed(self, *_args):
        """
        Commands : door, temprature, meteo
        """
        # Unsubscribe to the event when talking,
        # to avoid repetitions
        speechrecog.setVocabulary(wordList, True)
        try:
            memory.unsubscribeToEvent("MiddleTactilTouched",
                                      "HumanGreeter")
        except BaseException as ex:
            _logger.warning("onMiddleTouch: Got exception %s", ex)
            return
        isDoneSpeaking=False
        tts.say("Je vous écoute")

        memory.subscribeToEvent("WordRecognized",
            "HumanGreeter",
            "onSpeechRecognized")

        # Subscribe again to the event
        memory.subscribeToEvent("MiddleTactilTouched",
            "HumanGreeter",
            "onMiddleTouchSensed")
        
            
    def onFrontTouchSensed(self, *_args):
        """
        This will be called each time a face is
        detected.
        """
        # Unsubscribe to the event when talking,
        # to avoid repetitions
        
        try:
            memory.unsubscribeToEvent("FrontTactilTouched",
                                      "HumanGreeter")
        except BaseException as ex:
            _logger.warning("onFrontTouch: Got exception %s", ex)
            return
        isDoneSpeaking=False
        tts.say("Je vous écoute")

        memory.subscribeToEvent("WordRecognized",
            "HumanGreeter",
            "onSpeechRecognized")

        # Subscribe again to the event
        memory.subscribeToEvent("FrontTactilTouched",
            "HumanGreeter",
            "onMiddleTouchSensed")


    def say(self, sentence):
        """
        Says something
        """
        isDoneSpeaking=False
        tts.say(sentence)


    def set_hue_service(self, service):
        """
        Sets the hue service
        """
        self._hue = service

    def set_radio_service(self, service):
        """
        Sets the radio service
        """
        self._radio = service



    def set_teller_service(self, service):
        """
        Sets teller service
        """
        self._teller = service

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

    # Warning: HumanGreeter must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global HumanGreeter
    HumanGreeter = NaoTouchModule("HumanGreeter")

    # Create the Pelix framework
    framework = create_framework((# iPOPO
                                  'pelix.ipopo.core',

                                  # Shell bundles
                                  'pelix.shell.core',
                                  'pelix.shell.console',
                                  'pelix.shell.remote',
                                  'pelix.shell.ipopo',

                                  # HTTP Service
                                  'pelix.http.basic',

                                  # Remote Services
                                  'pelix.remote.dispatcher',
                                  'pelix.remote.registry',
                                  'pelix.remote.discovery.multicast',
                                  'pelix.remote.json_rpc',

                                  # ConfigurationAdmin
                                  'pelix.services.configadmin',
                                  'pelix.shell.configadmin',

                                  # MQTT
                                  'pelix.services.mqtt',

                                  # Nao
                                  'nao.shell',
                                  'nao.hue',
                                  'nao.radio',
                                  'nao.teller',
                                  'nao.binder'))
    framework.start()
    context = framework.get_bundle_context()

    # Register the ALModule as a service
    context.register_service("nao.core", HumanGreeter, {})

    # Instantiate basic components
    with use_ipopo(context) as ipopo:
        # ... Remote Shell
        ipopo.instantiate("ipopo-remote-shell-factory",
                          "ipopo-remote-shell",
                          {"pelix.shell.port": 9000})

        # ... HTTP Service on a random port
        ipopo.instantiate("pelix.http.service.basic.factory",
                          "pelix-http-basic",
                          {"pelix.http.port": 0})

        # Dispatcher servlet (for the multicast discovery)
        ipopo.instantiate("pelix-remote-dispatcher-servlet-factory",
                          "pelix-remote-dispatcher-servlet", {})

        # Multicast discovery
        ipopo.instantiate('pelix-remote-discovery-multicast-factory',
                          'pelix-remote-discovery-multicast', {})

        # JSON-RPC transport
        ipopo.instantiate("pelix-jsonrpc-exporter-factory",
                          "pelix-jsonrpc-exporter", {})
        ipopo.instantiate("pelix-jsonrpc-importer-factory",
                          "pelix-jsonrpc-importer", {})

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
