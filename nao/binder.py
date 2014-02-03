#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
Nao service binder
"""

# Module version
__version_info__ = (0, 1, 0)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

#-------------------------------------------------------------------------------

# Pelix
from pelix.ipopo.decorators import ComponentFactory, Requires, Instantiate, \
    Validate, Invalidate

#-------------------------------------------------------------------------------

@ComponentFactory('nao-service-binder')
@Requires('_hue', 'nao.hue')
@Requires('_radio', 'nao.radio')
@Requires('_teller', 'nao.teller')
@Requires('_nao', 'nao.core')
@Instantiate('nao-service-binder')
class HueMqttControll(object):
    """
    Provides a shell command to publish messages
    """
    def __init__(self):
        """
        Sets up members
        """
        # Injected service
        self._hue = None
        self._radio = None
        self._nao = None
        self._teller = None


    @Validate
    def validate(self, context):
        """
        All services are there
        """
        self._nao.set_hue_service(self._hue)
        self._nao.set_radio_service(self._radio)
        self._nao.set_teller_service(self._teller)


    @Invalidate
    def invalidate(self, context):
        """
        One service is gone
        """
        self._nao.set_hue_service(None)
        self._nao.set_radio_service(None)
        self._nao.set_teller_service(None)
