# Functional Main.py Implementation

This is a functional/procedural version of main.py (non-OOP approach).

```python
#!/usr/bin/env python3
"""
Frida Freq - Transit Art Display
Main controller orchestrating transit data, display, audio, and input
"""

import logging
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

import yaml

# Local modules (to be implemented)
from modules.transit import TransitFetcher
from modules.display import DisplayManager
from modules.audio import AudioManager
from modules.input import InputManager


# ============================================================================
# Global State
# ============================================================================

# Shared application state
transit_data: List[Dict[str, Any]] = []
current_route_index: int = 0
data_lock = threading.Lock()
shutdown_event = threading.Event()

# Module instances
transit_fetcher: Optional[TransitFetcher] = None
display_manager: Optional[DisplayManager] = None
audio_manager: Optional[AudioManager] = None
input_manager: Optional[InputManager] = None

# Config
config: Dict[str, Any] = {}

# Logger
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

def load_config(config_path: Path = Path("config.yaml")) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        logger.info("Copy config.example.yaml to config.yaml and edit")
        sys.exit(1)

    with open(config_path) as f:
        return yaml.safe_load(f)


# ============================================================================
# Initialization
# ============================================================================

def initialize_transit() -> Optional[TransitFetcher]:
    """Initialize transit fetcher (safe to fail - we can retry)"""
    try:
        fetcher = TransitFetcher(
            url=config['transit']['gtfsrt_url'],
            stop_ids=config['transit']['stop_ids'],
            routes=config['transit'].get('routes')
        )
        logger.info("Transit fetcher initialized")
        return fetcher
    except Exception as e:
        logger.error(f"Failed to initialize transit fetcher: {e}")
        return None


def initialize_display() -> Optional[DisplayManager]:
    """Initialize display (critical - fail if not available)"""
    try:
        display = DisplayManager(
            model=config['display']['model'],
            rotation=config['display'].get('rotation', 0)
        )
        logger.info("Display initialized")
        return display
    except Exception as e:
        logger.error(f"Failed to initialize display: {e}")
        return None


def initialize_audio() -> Optional[AudioManager]:
    """Initialize audio (nice to have - continue if fails)"""
    try:
        audio = AudioManager(
            voice=config['audio']['voice'],
            volume=config['audio']['volume'],
            template=config['audio']['voice_template']
        )
        logger.info("Audio initialized")
        return audio
    except Exception as e:
        logger.warning(f"Failed to initialize audio: {e}")
        return None


def initialize_input() -> Optional[InputManager]:
    """Initialize input handlers (nice to have - continue if fails)"""
    try:
        input_mgr = InputManager(
            announce_pin=config['buttons']['announce_pin'],
            cycle_pin=config['buttons']['cycle_pin'],
            on_announce=handle_announce_button,
            on_cycle=handle_cycle_button
        )
        logger.info("Input handlers initialized")
        return input_mgr
    except Exception as e:
        logger.warning(f"Failed to initialize input: {e}")
        return None


def initialize_all() -> bool:
    """Initialize all hardware and software modules"""
    global transit_fetcher, display_manager, audio_manager, input_manager

    logger.info("Initializing Frida Freq...")

    transit_fetcher = initialize_transit()
    display_manager = initialize_display()
    audio_manager = initialize_audio()
    input_manager = initialize_input()

    # Display is critical - fail if not available
    if display_manager is None:
        logger.error("Display initialization failed - cannot continue")
        return False

    return True


# ============================================================================
# Background Threads
# ============================================================================

def fetch_loop():
    """Background thread: periodically fetch transit data"""
    global transit_data

    interval = config['transit']['refresh_interval']

    while not shutdown_event.is_set():
        try:
            if transit_fetcher:
                arrivals = transit_fetcher.get_arrivals()

                with data_lock:
                    transit_data = arrivals

                logger.info(f"Fetched {len(arrivals)} arrivals")
            else:
                logger.warning("Transit fetcher not available")

        except Exception as e:
            logger.warning(f"Failed to fetch transit data: {e}")
            # Keep old data, retry on next interval

        # Sleep but wake up if shutdown requested
        shutdown_event.wait(timeout=interval)


def display_loop():
    """Background thread: periodically update display"""
    global current_route_index

    interval = config['display']['refresh_interval']

    while not shutdown_event.is_set():
        try:
            if display_manager:
                with data_lock:
                    data_to_display = transit_data.copy()
                    route_index = current_route_index

                if not data_to_display:
                    display_manager.show_message("No arrivals available")
                else:
                    display_manager.show_arrivals(data_to_display, route_index)

                logger.debug("Display updated")
            else:
                logger.warning("Display manager not available")

        except Exception as e:
            logger.error(f"Display update failed: {e}")
            # Continue - retry on next interval

        shutdown_event.wait(timeout=interval)


# ============================================================================
# Button Handlers
# ============================================================================

def handle_announce_button():
    """Called when announce button is pressed"""
    logger.info("Announce button pressed")

    if not audio_manager:
        logger.warning("Audio not available")
        return

    with data_lock:
        data = transit_data.copy()

    if not data:
        audio_manager.announce("No arrivals available")
        return

    # Announce next arrival
    next_arrival = data[0]
    audio_manager.announce_arrival(next_arrival)


def handle_cycle_button():
    """Called when cycle button is pressed"""
    global current_route_index

    logger.info("Cycle button pressed")

    with data_lock:
        if transit_data:
            current_route_index = (current_route_index + 1) % len(transit_data)
            logger.info(f"Cycled to route index {current_route_index}")

    # Immediately trigger display update
    try:
        if display_manager:
            with data_lock:
                data_to_display = transit_data.copy()
                route_index = current_route_index

            if data_to_display:
                display_manager.show_arrivals(data_to_display, route_index)
    except Exception as e:
        logger.error(f"Failed to update display on cycle: {e}")


# ============================================================================
# Main Run Logic
# ============================================================================

def initial_fetch_and_display():
    """Do initial fetch and display before starting background threads"""
    global transit_data

    # Initial fetch synchronously so we have data right away
    try:
        if transit_fetcher:
            arrivals = transit_fetcher.get_arrivals()
            with data_lock:
                transit_data = arrivals
            logger.info(f"Initial fetch: {len(arrivals)} arrivals")
    except Exception as e:
        logger.warning(f"Initial fetch failed: {e}")

    # Show initial display
    try:
        if display_manager:
            with data_lock:
                data_to_display = transit_data.copy()

            if data_to_display:
                display_manager.show_arrivals(data_to_display, 0)
            else:
                display_manager.show_message("Waiting for data...")
    except Exception as e:
        logger.error(f"Initial display failed: {e}")


def start_background_threads() -> tuple[threading.Thread, threading.Thread]:
    """Start fetch and display background threads"""
    fetch_thread = threading.Thread(
        target=fetch_loop,
        name="FetchThread",
        daemon=True
    )
    display_thread = threading.Thread(
        target=display_loop,
        name="DisplayThread",
        daemon=True
    )

    fetch_thread.start()
    display_thread.start()

    logger.info("Background threads started")

    return fetch_thread, display_thread


def run():
    """Main run loop - start background threads and monitor"""
    logger.info("Starting Frida Freq")

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


# ============================================================================
# Cleanup
# ============================================================================

def cleanup():
    """Graceful shutdown - cleanup all resources"""
    logger.info("Shutting down...")

    # Signal threads to stop
    shutdown_event.set()

    # Cleanup hardware
    if display_manager:
        try:
            display_manager.clear()
            display_manager.sleep()
        except Exception as e:
            logger.error(f"Display cleanup failed: {e}")

    if input_manager:
        try:
            input_manager.cleanup()
        except Exception as e:
            logger.error(f"Input cleanup failed: {e}")

    logger.info("Shutdown complete")


# ============================================================================
# Setup & Entry Point
# ============================================================================

def setup_logging(log_level: str = "INFO"):
    """Configure logging for the application"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/var/log/frida-freq.log')
        ]
    )


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Entry point"""
    global config

    setup_logging()
    setup_signal_handlers()

    config = load_config()

    # Initialize and run
    if not initialize_all():
        logger.error("Initialization failed - exiting")
        sys.exit(1)

    try:
        run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        cleanup()


if __name__ == "__main__":
    main()
```

## Key Architecture Features

### 1. Module-Level State
State is managed at the module level instead of in class instances:
- `transit_data` - shared list of arrivals
- `current_route_index` - which route to display
- `data_lock` - mutex for thread safety
- `shutdown_event` - coordination for graceful shutdown

### 2. Functional Organization
Code is organized into logical sections with pure functions:
- **Configuration**: Loading YAML config
- **Initialization**: One function per hardware module
- **Background Threads**: Separate fetch and display loops
- **Button Handlers**: Event-driven callbacks
- **Main Run Logic**: Sequential startup and coordination
- **Cleanup**: Resource teardown

### 3. Same Threading Model
- Uses `threading.Lock()` for shared state protection
- `threading.Event()` for shutdown coordination
- Separate background threads for fetch and display
- Main thread just monitors and waits for signals

### 4. Graceful Degradation
- Display is critical (fails hard if unavailable)
- Audio and buttons are optional (log warnings but continue)
- Network failures keep old data and retry

### 5. Clear Control Flow
The `main()` function shows the entire application flow:
1. Setup logging and signal handlers
2. Load configuration
3. Initialize all modules
4. Run main loop
5. Cleanup on exit

## Differences from OOP Version

**Advantages:**
- More Pythonic for script-style applications
- Easier to read top-to-bottom
- Less boilerplate/ceremony
- Functions can be tested independently
- Clear separation of concerns with section comments

**Tradeoffs:**
- Global state (though well-organized)
- Less encapsulation
- Can't easily instantiate multiple copies (not needed here)

## Usage

To use this code, copy the entire function into `main.py`.