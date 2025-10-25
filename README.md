# Frida Freq

A Raspberry Pi-powered transit arrival display featuring an e-paper screen and Billy-Bass-style audio announcements. Fetches real-time transit data from the WMATA API (Washington DC Metro), displays arrivals on e-paper, and announces them via text-to-speech.

## Features

- **Real-time Transit Data**: Fetches WMATA bus predictions for up-to-the-minute arrival times
- **E-paper Display**: Low-power, high-visibility Waveshare e-paper screen for crisp transit info
- **Voice Announcements**: TTS-powered audio announcements with configurable voice and templates (planned)
- **Interactive Controls**: Physical buttons to trigger announcements and cycle through routes (planned)
- **Development Mode**: Test without hardware - stubs out display, audio, and GPIO components
- **Graceful Degradation**: System continues running even if optional components (audio, buttons) fail
- **Configurable**: YAML-based configuration for easy customization

## Hardware Requirements

### Components

- **Compute**: Raspberry Pi Zero 2 W or Raspberry Pi 4
- **Display**: Waveshare 2.13" or 2.9" SPI e-paper display
- **Audio** (optional): MAX98357A I2S amplifier or USB audio device
- **Input** (optional): GPIO buttons for interaction
- **Power**: 5V power supply appropriate for your Pi model

### Wiring

**E-paper Display (SPI)**:
- Connect via SPI pins: 3V3, GND, MOSI, SCLK, CE0, DC, RST, BUSY
- See Waveshare documentation for specific pinout

**Buttons** (optional):
- GPIO 17: Announce button
- GPIO 27: Cycle routes button
- Use pull-up resistors to GND

**I2S Audio** (optional, for MAX98357A):
- LRC = GPIO 18
- BCLK = GPIO 19
- DIN = GPIO 21
- Connect +5V and GND
- Recommended: 100µF capacitor near amplifier

## Software Requirements

- Python 3.11 or higher
- Raspberry Pi OS (Debian-based) for production, or macOS/Linux for development
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- WMATA API key (free from [developer.wmata.com](https://developer.wmata.com/))

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/frida_freq.git
cd frida_freq
```

### 2. Install Dependencies

**Using uv (recommended)**:
```bash
uv sync
```

**Using pip**:
```bash
pip install -e .
```

### 3. Configure the Application

Copy the configuration template and edit it with your settings:

```bash
cp config.example.yaml config.yaml
nano config.yaml
```

**Configuration options**:

```yaml
development_mode: true  # Set to false when running on Raspberry Pi with hardware

transit:
  api_url: "https://api.wmata.com/NextBusService.svc/json/jPredictions"
  stop_id: "1001195"      # Single WMATA stop ID to monitor
  refresh_interval: 30    # Seconds between updates

display:
  model: "epd2in13_V4"    # Waveshare display model
  refresh_interval: 30    # Seconds between refreshes
  rotation: 0             # 0, 90, 180, or 270 degrees

audio:
  voice: "en_US-lessac-medium"  # Piper TTS voice
  volume: 80                     # 0-100
  voice_template: "Next arrival for {route} to {headsign} in {mins} minutes."

buttons:
  announce_pin: 17  # GPIO pin for announce button
  cycle_pin: 27     # GPIO pin for cycle button
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root with your WMATA API key:

```bash
echo "WMATA_API_KEY=your_api_key_here" > .env
```

Get a free API key from [developer.wmata.com](https://developer.wmata.com/).

## Usage

### Running the Application

```bash
python main.py
```

The application will:
1. Initialize logging (to `logs/frida-freq.log` and stdout)
2. Setup signal handlers for graceful shutdown (SIGINT, SIGTERM)
3. Load configuration from `config.yaml`
4. Initialize hardware modules (display, audio, buttons)
5. Start background threads for data fetching and display updates

### Systemd Service (Optional)

To run Frida Freq as a system service that starts on boot:

```bash
# Copy service file (to be created)
sudo cp systemd/frida-freq.service /etc/systemd/system/
sudo systemctl enable frida-freq
sudo systemctl start frida-freq
```

Check status:
```bash
sudo systemctl status frida-freq
```

View logs:
```bash
journalctl -u frida-freq -f
```

## Project Structure

```
frida_freq/
├── main.py                     # Application entry point
├── pyproject.toml              # Python project configuration
├── config.yaml                 # User configuration (gitignored)
├── config.example.yaml         # Configuration template
├── .env                        # API keys (gitignored)
├── modules/
│   ├── config.py              # Configuration loading
│   ├── logging_config.py      # Logging setup
│   ├── signal_handlers.py     # Graceful shutdown handlers
│   ├── frida.py               # Central state management and orchestration
│   ├── transit.py             # WMATA API integration (implemented)
│   ├── display.py             # E-paper rendering (stubbed in dev mode)
│   ├── audio.py               # TTS announcements (planned)
│   └── input.py               # Button handling (planned)
├── logs/                       # Application logs
├── functional_main.md          # Reference architecture documentation
└── CLAUDE.md                   # Instructions for Claude Code
```

## Architecture

Frida Freq uses a **hybrid functional/class-based architecture** with:
- Module-level global state in `modules/frida.py` (shared transit data, threading primitives)
- Manager classes for encapsulated functionality (TransitManager, DisplayManager)
- Threading with locks for concurrency safety (`data_lock`, `shutdown_event`)
- Separate background threads for data fetching and display updates
- Development mode flag to stub out hardware for local testing
- Graceful degradation: display is critical, audio/buttons are optional

See `functional_main.md` for detailed reference implementation and `CLAUDE.md` for architecture details.

## Development Status

**Implemented**:
- Core infrastructure (logging, config, signal handling)
- WMATA API integration with real-time bus predictions
- Threading model with background fetch loop
- Development mode for testing without hardware
- Manager-based architecture

**In Progress**:
- E-paper display rendering implementation
- Audio announcement system (Piper TTS)
- GPIO button input handling

**Future Enhancements**:
- Servo/stepper motor for "singing fish" animation
- Sound effects (chimes, door closing, station ambience)
- Multiple stop rotation
- Web interface for configuration and monitoring
- Offline mode with static art display

## Troubleshooting

**Display not working**:
- Verify SPI is enabled: `sudo raspi-config` → Interface Options → SPI
- Check wiring connections
- Ensure correct display model in config

**No audio output**:
- Check I2S or USB audio configuration
- Verify volume settings
- Audio is optional - system continues without it

**Can't fetch transit data**:
- Verify your WMATA API key is set in `.env`
- Check that the stop ID is valid (use [WMATA's API docs](https://developer.wmata.com/) to find stop IDs)
- Ensure your API key has permission to access the NextBus API
- Review logs in `logs/frida-freq.log` for detailed error messages

**Development mode issues**:
- Set `development_mode: true` in `config.yaml` to test without hardware
- In dev mode, display and GPIO components are stubbed
- Transit API calls still happen in dev mode (requires API key)

## References

- [WMATA API Documentation](https://developer.wmata.com/)
- [WMATA NextBus API](https://developer.wmata.com/docs/services/5476365068a048e3fca1cd6d/)
- [Waveshare E-Paper Documentation](https://www.waveshare.com/wiki/E-Paper)
- [Piper TTS](https://github.com/rhasspy/piper)
- [GPIO Zero Documentation](https://gpiozero.readthedocs.io/)

## License

[Your chosen license - e.g., MIT, GPL-3.0, etc.]

## Acknowledgments

- Inspired by the joy of transit and the absurdity of singing fish
- Built for transit enthusiasts who want real-time arrivals with personality

---

**Note**: This project is under active development. Features and documentation may change.
