# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: Frida Freq - Transit Art Display

A Raspberry Pi-powered transit arrival display featuring an e-paper screen and Billy-Bass-style audio announcements. Currently implements WMATA API integration for Washington DC Metro bus arrivals.

## Running the Application

```bash
# Run the main application
python main.py

# The app will:
# 1. Setup logging to logs/frida-freq.log and stdout
# 2. Setup signal handlers for graceful shutdown (SIGINT, SIGTERM)
# 3. Load config from config.yaml
# 4. Initialize hardware modules (display, transit manager)
# 5. Start background threads for fetching and displaying transit data
```

## Development Environment

- **Runtime**: Python 3.11+
- **Package Manager**: uv (uv.lock present) or pip
- **Dependencies**: pyyaml, python-dotenv, certifi (see [pyproject.toml](pyproject.toml))
- **Target Platform**: Raspberry Pi OS (Debian-based)
- **Environment**: Requires `.env` file with `WMATA_API_KEY` for transit data

## Current Architecture

### Hybrid Functional/Class-Based Design

The codebase uses a **hybrid approach** combining module-level state management (in [modules/frida.py](modules/frida.py)) with manager classes for individual components:

**Key architectural decisions:**
- Module-level global state in [modules/frida.py](modules/frida.py) (transit_data, current_route_index, etc.)
- Manager classes for encapsulated functionality (TransitManager, DisplayManager)
- Threading with locks for concurrency (data_lock, shutdown_event)
- Separate background threads for fetch and display loops
- Development mode flag to stub out hardware for local testing

### Module Structure

```
modules/
├── __init__.py
├── config.py           # YAML configuration loading
├── logging_config.py   # Centralized logging setup
├── signal_handlers.py  # SIGINT/SIGTERM handlers
├── frida.py           # Central state + orchestration (init, run, cleanup)
├── transit.py         # TransitManager - WMATA API integration
└── display.py         # DisplayManager - e-paper display (stubbed in dev mode)
```

**[modules/frida.py](modules/frida.py)** - Central orchestration module:
- Global state: `transit_data`, `current_route_index`, `data_lock`, `shutdown_event`, `config`, `DEVELOPMENT_MODE`
- Manager instances: `transit_manager`, `display_manager`, `audio_manager`, `input_manager`
- `init_frida()` - Initialize all managers
- `run_frida()` - Start background threads and monitor
- `cleanup_frida()` - Graceful shutdown
- State is shared via module-level imports: `import modules.frida as Frida`

**[modules/transit.py](modules/transit.py)** - WMATA API integration:
- `TransitManager` class handles fetching real-time bus predictions
- Uses WMATA NextBusService API (not generic GTFS-RT)
- `get_arrivals()` returns list of dicts: `[{route, headsign, arrival_in_min}, ...]`
- `fetch_loop()` runs in background thread, updates shared `transit_data`
- Requires `WMATA_API_KEY` environment variable from `.env`

**[modules/display.py](modules/display.py)** - E-paper display manager:
- `DisplayManager` class (currently stubbed for development)
- `init_display_manager(model, rotation)` - Hardware initialization
- Respects `DEVELOPMENT_MODE` flag from config
- `display_loop()` will run in background thread (currently empty)

## Configuration Format

[config.yaml](config.yaml) structure:

```yaml
development_mode: true  # Set false for production on Pi

transit:
  api_url: "https://api.wmata.com/NextBusService.svc/json/jPredictions"
  stop_id: "1001195"  # Single WMATA stop ID
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

**Important**: Copy [config.example.yaml](config.example.yaml) to `config.yaml` and customize. Create `.env` with `WMATA_API_KEY=your_key_here`.

## Module Access Pattern

Other modules access shared state via:
```python
import modules.frida as Frida

# Access state
with Frida.data_lock:
    arrivals = Frida.transit_data

# Access config
api_url = Frida.config['transit']['api_url']

# Access logger
Frida.logger.info("Message")

# Check development mode
if Frida.DEVELOPMENT_MODE:
    # stub hardware
```

## Threading Model

Implemented in [modules/frida.py](modules/frida.py):
- **fetch_loop()**: Background thread in `transit_manager.fetch_loop()` - fetches transit data periodically
- **display_loop()**: Background thread in `display_manager.display_loop()` - updates e-paper display
- **Main thread**: Waits for shutdown signal in `run_frida()`
- **Synchronization**: `data_lock` (threading.Lock) protects shared state, `shutdown_event` (threading.Event) coordinates shutdown

## Implementation Status

**Implemented:**
- Core infrastructure (logging, config, signal handling)
- WMATA API integration with real-time bus predictions
- Threading model with background fetch loop
- Development mode for testing without hardware
- Manager-based architecture for display (stubbed)

**TODO:**
- Complete display rendering implementation (Waveshare e-paper)
- Audio module (Piper TTS)
- Input module (GPIO buttons)
- Button handlers for announce and cycle actions

## Hardware Details

### Components
- **Compute**: Raspberry Pi Zero 2 W or Pi 4
- **Display**: Waveshare 2.13" or 2.9" SPI e-paper
- **Audio**: MAX98357A I2S amp or USB audio (optional)
- **Input**: GPIO buttons (optional)

### Critical vs. Optional Hardware
- **Display**: Critical - `init_frida()` fails if unavailable (unless `DEVELOPMENT_MODE = true`)
- **Audio**: Optional - log warning but continue
- **Buttons**: Optional - log warning but continue
- **Network/Transit API**: Optional - keep old data and retry

## Error Handling Philosophy

- **Graceful degradation**: Keep system running even if some components fail
- **Retry with backoff**: For network/API failures (keep old data, retry on next interval)
- **Preserve lifespan**: Reasonable e-paper refresh rates
- **Logging levels**:
  - INFO: Normal operations, successful fetches
  - WARNING: Recoverable issues (API timeout, retrying)
  - ERROR: Serious problems (can't initialize critical hardware)
  - DEBUG: Detailed API responses, troubleshooting

## References

- **Detailed functional architecture**: See [functional_main.md](functional_main.md) for reference implementation
- **WMATA API**: https://developer.wmata.com/
- **Waveshare e-paper**: https://www.waveshare.com/wiki/E-Paper
- **Piper TTS**: https://github.com/rhasspy/piper
