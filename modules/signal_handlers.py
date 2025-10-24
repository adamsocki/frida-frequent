"""
Signal handlers for graceful shutdown
"""
import logging
import signal
import sys
from typing import Optional, Callable

logger = logging.getLogger(__name__)


def setup_signal_handlers(cleanup_callback: Optional[Callable] = None):
    """
    Setup signal handlers for graceful shutdown

    This function registers handlers that will be called when the program
    receives interrupt signals (like Ctrl+C or systemd stop commands).
    This allows us to clean up resources before exiting.

    Args:
        cleanup_callback: Optional function to call before exit for resource cleanup
                         (e.g., clearing the display, releasing GPIO pins)
    """

    # Define the signal handler as a nested function
    # We do this because:
    # 1. The handler needs access to cleanup_callback from the outer scope (closure)
    # 2. Signal handlers must have signature: (signum, frame) -> None
    # 3. This keeps the handler logic encapsulated within setup_signal_handlers
    def signal_handler(signum, frame):
        """
        Called when SIGINT (Ctrl+C) or SIGTERM (systemd stop) is received

        Args:
            signum: The signal number that was received
            frame: Current stack frame (not used, but required by signal API)
        """
        logger.info(f"Received signal {signum}")

        # Call cleanup callback if one was provided
        # This allows the caller to clean up resources (display, GPIO, etc.)
        if cleanup_callback:
            try:
                cleanup_callback()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

        # Exit the program gracefully
        sys.exit(0)

    # Register our handler for common termination signals
    # SIGINT: Sent when user presses Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # SIGTERM: Sent by systemd or kill command for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Signal handlers configured for SIGINT and SIGTERM")
