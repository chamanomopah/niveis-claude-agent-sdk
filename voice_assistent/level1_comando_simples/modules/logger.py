"""
NERO Voice Assistant - Logger Module

Rich terminal logging with color-coded states for the voice assistant pipeline.
"""

from rich.console import Console
from rich.text import Text
from datetime import datetime
from typing import Optional


class NeroLogger:
    """Rich console logger with color-coded state output."""

    # Color scheme for different log levels
    COLORS = {
        "INFO": "blue",
        "LISTENING": "yellow",
        "RECORDING": "red",
        "TRANSCRIBING": "cyan",
        "TRANSCRIPT": "white",
        "STOP_WORD": "green",
        "AGENT": "magenta",
        "TOOL": "cyan",
        "COMPLETE": "green",
        "TTS": "purple",
        "DONE": "green",
        "ERROR": "red",
        "WARNING": "yellow",
        "DEBUG": "dim white",
    }

    # Emoji indicators for each state
    EMOJIS = {
        "INFO": "ℹ️",
        "LISTENING": "🔊",
        "RECORDING": "🎙️",
        "TRANSCRIBING": "📝",
        "TRANSCRIPT": "💬",
        "STOP_WORD": "✋",
        "AGENT": "🤖",
        "TOOL": "🔧",
        "COMPLETE": "✅",
        "TTS": "🔈",
        "DONE": "🏁",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "DEBUG": "🔍",
    }

    def __init__(self, verbose: bool = False):
        """Initialize the logger with a Rich console.

        Args:
            verbose: Enable debug-level logging
        """
        import sys
        import io

        # Set UTF-8 encoding for Windows console
        if sys.platform == "win32":
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")

        self.console = Console(legacy_windows=False)
        self.verbose = verbose

    def _get_timestamp(self) -> str:
        """Get formatted timestamp for log messages.

        Returns:
            Formatted timestamp string (HH:MM:SS)
        """
        return datetime.now().strftime("%H:%M:%S")

    def log(
        self,
        level: str,
        message: str,
        emoji: Optional[str] = None,
        color: Optional[str] = None,
    ) -> None:
        """Log a message with specified level and formatting.

        Args:
            level: Log level (INFO, ERROR, AGENT, etc.)
            message: Message content
            emoji: Optional emoji override
            color: Optional color override
        """
        # Get defaults from level
        emoji = emoji or self.EMOJIS.get(level, "•")
        color = color or self.COLORS.get(level, "white")

        # Don't show debug logs unless verbose mode
        if level == "DEBUG" and not self.verbose:
            return

        # Format timestamp
        timestamp = self._get_timestamp()

        # Build rich text
        text = Text()
        text.append(timestamp, style="dim")
        text.append(" ")
        text.append(f"[{level}]", style=color)
        text.append(" ")
        text.append(f"{emoji} ", style=color)
        text.append(message)

        self.console.print(text)

    def info(self, message: str) -> None:
        """Log informational message."""
        self.log("INFO", message)

    def listening(self, message: str) -> None:
        """Log wake word listening state."""
        self.log("LISTENING", message)

    def recording(self, message: str) -> None:
        """Log audio recording state."""
        self.log("RECORDING", message)

    def transcribing(self, message: str) -> None:
        """Log transcription state."""
        self.log("TRANSCRIBING", message)

    def transcript(self, message: str) -> None:
        """Log transcribed text."""
        self.log("TRANSCRIPT", f'"{message}"', emoji="💬")

    def stop_word(self, message: str) -> None:
        """Log stop word detection."""
        self.log("STOP_WORD", message)

    def agent(self, message: str) -> None:
        """Log Claude agent processing."""
        self.log("AGENT", message)

    def tool(self, tool_name: str, message: str = "") -> None:
        """Log tool execution."""
        msg = f"Using {tool_name}"
        if message:
            msg += f": {message}"
        self.log("TOOL", msg)

    def complete(self, message: str) -> None:
        """Log task completion."""
        self.log("COMPLETE", message)

    def tts(self, message: str) -> None:
        """Log text-to-speech generation."""
        self.log("TTS", message)

    def done(self, message: str = "") -> None:
        """Log return to idle state."""
        if message:
            self.log("DONE", message)
        else:
            self.log("DONE", "Returning to idle state")

    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Log error message with optional exception details.

        Args:
            message: Error description
            exception: Optional exception object for details
        """
        self.log("ERROR", message)
        if exception and self.verbose:
            self.console.print(f"  [dim]Exception: {exception}[/dim]")

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.log("WARNING", message)

    def debug(self, message: str) -> None:
        """Log debug message (only in verbose mode)."""
        self.log("DEBUG", message)

    def print_banner(self) -> None:
        """Print startup banner with ASCII art."""
        banner = """
╔════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███╗   ██╗████████╗██████╗ ███████╗██████╗ ██╗   ██╗     ║
║   ████╗  ██║╚══██╔══╝██╔══██╗██╔════╝██╔══██╗╚██╗ ██╔╝     ║
║   ██╔██╗ ██║   ██║   ██████╔╝█████╗  ██████╔╝ ╚████╔╝      ║
║   ██║╚██╗██║   ██║   ██╔══██╗██╔══╝  ██╔══██╗  ╚██╔╝       ║
║   ██║ ╚████║   ██║   ██║  ██║███████╗██║  ██║   ██║        ║
║   ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝        ║
║                                                              ║
║              Voice Assistant v1.0 - Claude Agent SDK           ║
║                                                              ║
╚════════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="bold cyan")
        self.info("Initializing NERO voice assistant...")
        self.info("Press Ctrl+C at any time to exit gracefully")

    def print_section(self, title: str) -> None:
        """Print a section divider.

        Args:
            title: Section title
        """
        self.console.print()
        self.console.print(f"══ {title} ══", style="bold cyan")
        self.console.print()
