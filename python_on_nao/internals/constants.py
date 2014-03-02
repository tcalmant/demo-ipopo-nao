#!/usr/bin/env python
# -- Content-Encoding: UTF-8 --
"""
Nao services constants
"""

# Module version
__version_info__ = (0, 1, 0)
__version__ = ".".join(str(x) for x in __version_info__)

# Documentation strings format
__docformat__ = "restructuredtext en"

#-------------------------------------------------------------------------------

# Standard library
import sys

#-------------------------------------------------------------------------------

def register_almodule(name, module):
    """
    Registers an ALModule as a global in the main module.
    """
    setattr(sys.modules['__main__'], name, module)


def unregister_almodule(name):
    """
    Unregisters an ALModule from the main module.
    """
    delattr(sys.modules['__main__'], name)

#-------------------------------------------------------------------------------

SERVICE_TTS = "nao.internals.tts"
"""
Specification of the Text-To-Speech service:

- say(sentence): Nao says the given sentence. Blocks until the robot is
  authorized to speak.
- resume(): Authorize Nao to say something (resume the waiting say() calls)
- pause(): Let the next TTS calls wait for the next call to resume()
"""

SERVICE_SPEECH = "nao.internals.speech"
"""
Specification of the Speech Recognition service
"""
