"""
Frida Freq - Transit Art Display
Main application entry point
"""
from modules.logging_config import setup_logging
from modules.signal_handlers import setup_signal_handlers
from modules.config import load_config
from modules.frida import init_frida
import sys


def main():
    global config

    """Entry point"""
    # Setup logging
    logger = setup_logging(log_level="INFO")

    logger.info("Starting Frida Freq...")
    logger.info("Yoca")

    setup_signal_handlers()

    config = load_config()

    # Initialize and run
    if not init_frida():
        logger.error("Initialization failed - exiting")
        sys.exit(1)



if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
