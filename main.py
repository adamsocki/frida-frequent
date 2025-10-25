"""
Frida Freq - Transit Art Display
Main application entry point
"""

import modules.frida as Frida
from modules.logging_config import setup_logging
from modules.signal_handlers import setup_signal_handlers
from modules.config import load_config
from modules.frida import init_frida, run_frida, cleanup_frida
import sys


def main():
    """Entry point"""
    # Setup logging
    Frida.logger = setup_logging(log_level="INFO")

    Frida.logger.info("Starting Frida Freq...")
    Frida.logger.info("Yoca")

    setup_signal_handlers()

    # Load config into Frida module
    Frida.config = load_config()

    # Initialize and run
    if not init_frida():
        Frida.logger.error("Initialization failed - exiting")
        sys.exit(1)

    try:
        run_frida()
    except Exception as ex:
        Frida.logger.error(f"Fatal error: {ex}", exc_info=True)
        sys.exit(1)
    finally:
        cleanup_frida()


if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
