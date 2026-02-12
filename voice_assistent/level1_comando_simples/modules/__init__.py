"""
NERO Voice Assistant - Modules Package

A modular voice-controlled AI assistant using Claude Agent SDK.
"""

__version__ = "1.0.0"
__author__ = "NERO Project"

from .logger import NeroLogger
from .stt_fraco import STTFraco
from .stt_forte import STTForte
from .tts import TTS
from .agent_handler import AgentHandler

__all__ = [
    "NeroLogger",
    "STTFraco",
    "STTForte",
    "TTS",
    "AgentHandler",
]
