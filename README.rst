Nao-iPOPO Demonstration
#######################

Nao's code of a demonstration project for the
`Eclipse IoT Day Grenoble 2014 <https://wiki.eclipse.org/Eclipse_IoT_Day_Grenoble_2014>`_.
`[Video]  <http://youtu.be/4vBSJ7csp8g>`_.

Nao is a robot by `Aldebaran Robotics <http://www.aldebaran-robotics.com/>`_.

This project is based on `iPOPO <https://ipopo.coderxpress.net>`_, a
Service-Oriented Component Model (SOCM) framework in Python, to wrap Nao
API (ALModule, ALProxy, ...) into different components which provide and
consume services.

It uses MQTT to send and receive message to/from
`OpenHAB <http://www.openhab.org/>`_, to control Home Automation devices, like
`Philips Hue <http://www.meethue.com/>`_.

Information about this project will be available on the
`wiki of iPOPO <https://ipopo.coderxpress.net/wiki/doku.php?id=contrib:eclipse_iot_2014>`_.


Installation
************

All installation operation are done in the ``/home/nao`` folder

iPOPO and its dependencies
==========================

We consider that no package installation tool is present on the robot, else a
simple ``pip install iPOPO paho-mqtt`` will be sufficient

Preparation
-----------

Create a ``python-libs`` folder in ``/home/nao``.

iPOPO
-----

We will use the development version of iPOPO.

#. Download https://github.com/tcalmant/ipopo/archive/master.zip
#. Extract it
#. Move the ``pelix`` into ``python-libs``
#. Delete the rest

Paho MQTT
---------

Paho MQTT is the new name of the Mosquitto client library, as it is now part
of the Eclipse project.

#. Download the package from https://pypi.python.org/pypi/paho-mqtt
#. Extract it
#. Move ``src/paho`` into ``python-libs``


Demo Project
============

You must have a MQTT server and OpenHAB up and running for this demonstration
to work.

#. Download this project:
   https://github.com/tcalmant/demo-ipopo-nao/archive/master.zip
#. Extract it
#. Copy the content of ``python_on_nao`` in ``/home/nao/demo-ipopo-nao``.
#. Run the ``main.py`` file from the ``/home/nao/demo-ipopo-nao``
   folder.
#. On the first run, create a configuration to connect to the MQTT server, using
   the Pelix shell:::
   
     config.create mqtt.connector host=<mqtt-host> port=<mqtt-port>
