# CLAUDE.md

This file prov
ides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: Frida Freq - Transit Art Display

A Raspberry Pi-powered transit arrival display featuring an e-paper screen and Billy-Bass-style audio announcements. Fetches GTFS-Realtime data, displays arrivals on e-paper, and announces them via TTS.

## Running the Application

```bash
# Run the main application
python main.py

# The app will:
# 1. Setup logging to logs/frida-freq.log and stdout
# 2. Setup signal handlers for graceful shutdown (SIGINT, SIGTERM)
# 3. Load config from config.yaml
# 4. Initialize hardware modules (currently returns False - stub)
```

## Development Environment

- **Runtime**: Python 3.11+
- **Package Manager**: uv (uv.lock present) or pip
- **Dependencies**: See pyproject.toml (currently only pyyaml)
- **Target Platform**: Raspberry Pi OS (Debian-based)

## Current Architecture

### Functional/Procedural Design

The codebase uses a **functional approach** with module-level state rather than OOP. This is documented in `functional_main.md` which contains a detailed reference implementation.

**Key architectural decisions:**
- Module-level global state for shared data (transit_data, current_route_index, etc.)
- Threading with locks for concurrency (data_lock, shutdown_event)
- Separate background threads for fetch and display loops
- Event-driven button handlers as callbacks
- Graceful degradation: display is critical, audio/buttons are optional

### Current Module Structure

```
modules/
├── __init__.py
├── config.py           # YAML configuration loading
├── logging_config.py   # Centralized logging setup
├── signal_handlers.py  # SIGINT/SIGTERM handlers with cleanup callbacks
└── frida.py           # Hardware/module initialization (stub)
```

**config.py** (`modules/config.py:9`):
- `load_config(config_path: Path = Path("config.yaml"))` - Loads YAML config, exits if missing
- Returns dict with configuration structure

**logging_config.py** (`modules/logging_config.py:37`):
- `setup_logging(log_level: str = "INFO", log_file: str = "logs/frida-freq.log")` - Configures logging
- Creates log directory if needed
- Logs to both stdout and file
- Returns logger named 'frida_freq'
- Other modules get logger via: `logging.getLogger('frida_freq')`

**signal_handlers.py** (`modules/signal_handlers.py:12`):
- `setup_signal_handlers(cleanup_callback: Optional[Callable] = None)` - Registers SIGINT/SIGTERM handlers
- Calls optional cleanup callback before exit
- Allows graceful shutdown for resource cleanup (display, GPIO, etc.)

**frida.py** (`modules/frida.py:3`):
- `init_frida() -> bool` - Initialize hardware and software modules (currently stub returning False)
- Should initialize: transit_fetcher, display_manager, audio_manager, input_manager (not yet implemented)

**main.py**:
- Entry point that orchestrates: logging → signal handlers → config → initialization
- Currently exits with code 1 since init_frida() returns False

## Configuration Format

Expected `config.yaml` structure:

```yaml
transit:
  gtfsrt_url: "https://api.example.com/gtfs-rt"
  stop_ids: ["12345"]
  routes: ["A"]  # optional filter
  refresh_interval: 30

display:
  model: "epd2in13_V4"
  refresh_interval: 30
  rotation: 0

audio:
  voice: "en_US-lessac-medium"
  volume: 80
  voice_template: "Next arrival for {route} to {headsign} in {mins} minutes."

buttons:
  announce_pin: 17
  cycle_pin: 27
```

## Modules to Implement

See `functional_main.md` for detailed reference implementation. Core modules needed:

1. **Transit Module** (`modules/transit.py`) - GTFS-RT fetching/parsing
2. **Display Module** (`modules/display.py`) - Waveshare e-paper rendering
3. **Audio Module** (`modules/audio.py`) - Piper TTS/eSpeak
4. **Input Module** (`modules/input.py`) - GPIO button handling via gpiozero

## Threading Model

From `functional_main.md`:
- **fetch_loop()**: Background thread periodically fetching transit data
- **display_loop()**: Background thread updating e-paper display
- **Main thread**: Monitors and waits for shutdown signal
- **Synchronization**: Use `data_lock` (threading.Lock) for shared state, `shutdown_event` (threading.Event) for coordination

## Hardware Details

### Components
- **Compute**: Raspberry Pi Zero 2 W or Pi 4
- **Display**: Waveshare 2.13" or 2.9" SPI e-paper
- **Audio**: MAX98357A I2S amp (GPIO18/19/21) or USB audio
- **Input**: GPIO buttons (announce + cycle)

### Wiring

**E-paper (SPI)**:
- 3V3, GND, MOSI, SCLK, CE0, DC, RST, BUSY

**Buttons**:
- GPIO pins with pull-up resistors to GND

**I2S Audio**:
- LRC = GPIO18, BCLK = GPIO19, DIN = GPIO21
- +5V and GND to amplifier
- 100µF capacitor near amp recommended

### Critical vs. Optional Hardware
- **Display**: Critical - fail if unavailable
- **Audio**: Optional - log warning but continue
- **Buttons**: Optional - log warning but continue
- **Network/Transit API**: Optional - keep old data and retry

## Error Handling Philosophy

- **Graceful degradation**: Keep system running even if some components fail
- **Retry with backoff**: For network/API failures
- **Preserve lifespan**: Reasonable e-paper refresh rates (partial refresh preferred)
- **Logging levels**:
  - INFO: Normal operations
  - WARNING: Recoverable issues (API timeout, retrying)
  - ERROR: Serious problems (can't initialize critical hardware)
  - DEBUG: Detailed troubleshooting

## Code Style

- Follow PEP 8
- Use type hints (as shown in existing modules)
- Docstrings for public functions
- Keep modules focused and decoupled

## Planned Directory Structure

```
frida_freq/
├── main.py
├── pyproject.toml
├── config.yaml (gitignored)
├── modules/
│   ├── config.py, logging_config.py, signal_handlers.py, frida.py
│   ├── transit.py, display.py, audio.py, input.py (to implement)
├── tests/ (to create)
├── assets/ (fonts, sounds, images)
├── cad/ (3D models)
└── systemd/ (service unit)
```

## Future Enhancements
- Motion: Add servo/stepper for "singing fish" effect
- Sound effects: Chimes, door closing sounds, station ambience
- Multiple stops: Rotate through several locations
- Web interface: Configuration and monitoring
- Offline mode: Display static art when transit unavailable

## References

- **Detailed functional architecture**: See `functional_main.md`
- **GTFS-Realtime**: https://gtfs.org/realtime/
- **Waveshare e-paper**: https://www.waveshare.com/wiki/E-Paper
- **Piper TTS**: https://github.com/rhasspy/piper
- **GPIO Zero**: https://gpiozero.readthedocs.io/