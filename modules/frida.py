import logging
import threading
import time
from typing import Optional, Any, Dict, List

from modules.display import DisplayManager
from modules.transit import TransitManager

# Shared application state
transit_data: List[Dict[str, Any]] = []
current_route_index: int = 0
data_lock = threading.Lock()
shutdown_event = threading.Event()

# Module instances (if any)
transit_manager: TransitManager = None
display_manager: DisplayManager = None
audio_manager: Optional[Any] = None
input_manager: Optional[Any] = None

# Config
config: Dict[str, Any] = {}

# Development mode (set from config)
DEVELOPMENT_MODE: bool = False

# Logger
logger = logging.getLogger('frida_freq')


def init_frida() -> bool:
    """Initialize Frida Freq hardware and software modules"""
    global transit_manager, display_manager, audio_manager, input_manager, DEVELOPMENT_MODE

    logger.info("Initializing Frida Freq...")

    # Set development mode from config
    DEVELOPMENT_MODE = config.get('development_mode', False)
    if DEVELOPMENT_MODE:
        logger.info("Running in DEVELOPMENT MODE - hardware will be stubbed")

    transit_manager = TransitManager()
    transit_manager.init_transit_manager()

    display_manager = DisplayManager()
    # Display is critical - fail if not available
    if not display_manager.init_display_manager(model="epd2in13_V4", rotation=0):
        logger.error("Display initialization failed - cannot continue")
        return False

    # audio_manager = AudioManager()
    # audio_manager.initialize_audio_manager()
    # input_manager = InputManager()
    # input_manager.initialize_input_manager()



    return True

def initial_fetch_and_display():
    """Do initial fetch and display before starting background threads"""
    if transit_manager:
        logger.info("checking Transit Manager...")
    else:
        logger.info("no Transit Manager")

def start_background_threads() -> tuple[threading.Thread, threading.Thread]:
    """Start fetch and display background threads"""
    fetch_thread = threading.Thread(
        target=transit_manager.fetch_loop,
        name="FetchThread",
        daemon=True
    )
    display_thread = threading.Thread(
        target=display_manager.display_loop,
        name="DisplayThread",
        daemon=True
    )

    fetch_thread.start()
    display_thread.start()

    logger.info("Background threads started")

    return fetch_thread, display_thread


def run_frida():
    """Main run loop - start background threads and monitor"""
    logger.info("Starting Frida Freq...")

    initial_fetch_and_display()

    fetch_thread, display_thread = start_background_threads()

    # Main thread just waits for shutdown signal
    try:
        while not shutdown_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")

    # Wait for threads to finish
    shutdown_event.set()
    fetch_thread.join(timeout=5)
    display_thread.join(timeout=5)





def cleanup_frida():
    """Graceful shutdown - cleanup all resources"""

    logger = logging.getLogger('frida_freq')
    logger.info("Shutting down Frida Freq...");