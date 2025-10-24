# Frida Freq

A Raspberry Pi-powered transit arrival display featuring an e-paper screen and Billy-Bass-style audio announcements. Fetches real-time GTFS data, displays arrivals on e-paper, and announces them via text-to-speech.

## Features

- **Real-time Transit Data**: Fetches GTFS-Realtime feeds for up-to-the-minute arrival predictions
- **E-paper Display**: Low-power, high-visibility Waveshare e-paper screen for crisp transit info
- **Voice Announcements**: TTS-powered audio announcements with configurable voice and templates
- **Interactive Controls**: Physical buttons to trigger announcements and cycle through routes
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
- Raspberry Pi OS (Debian-based)
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip

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
cp config.template.yaml config.yaml
nano config.yaml
```

**Configuration options**:

```yaml
transit:
  gtfsrt_url: "https://api.example.com/gtfs-rt"  # Your GTFS-RT feed URL
  stop_ids: ["12345"]                             # Stop IDs to monitor
  routes: ["A", "B"]                              # Optional route filter
  refresh_interval: 30                            # Seconds between updates

display:
  model: "epd2in13_V4"                            # Waveshare display model
  refresh_interval: 30                            # Seconds between refreshes
  rotation: 0                                     # 0, 90, 180, or 270 degrees

audio:
  voice: "en_US-lessac-medium"                    # Piper TTS voice
  volume: 80                                      # 0-100
  voice_template: "Next arrival for {route} to {headsign} in {mins} minutes."

buttons:
  announce_pin: 17                                # GPIO pin for announce button
  cycle_pin: 27                                   # GPIO pin for cycle button
```

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
├── config.template.yaml        # Configuration template
├── modules/
│   ├── config.py              # Configuration loading
│   ├── logging_config.py      # Logging setup
│   ├── signal_handlers.py     # Graceful shutdown handlers
│   ├── frida.py               # Hardware initialization
│   ├── transit.py             # GTFS-RT data fetching (planned)
│   ├── display.py             # E-paper rendering (planned)
│   ├── audio.py               # TTS announcements (planned)
│   └── input.py               # Button handling (planned)
├── logs/                       # Application logs
├── assets/                     # Fonts, sounds, images
├── cad/                        # 3D printable case designs
└── tests/                      # Unit tests
```

## Architecture

Frida Freq uses a **functional/procedural architecture** with:
- Module-level global state for shared data
- Threading with locks for concurrency safety
- Separate background threads for data fetching and display updates
- Event-driven button handlers
- Graceful degradation: display is critical, audio/buttons are optional

See `functional_main.md` for detailed reference implementation.

## Development Status

**Current**: Early development - core infrastructure in place (logging, config, signal handling)

**In Progress**:
- Transit data fetching module
- E-paper display rendering
- Audio announcement system
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
- Verify GTFS-RT URL is accessible
- Check stop IDs are valid for your transit agency
- Review logs in `logs/frida-freq.log`

## References

- [GTFS Realtime Specification](https://gtfs.org/realtime/)
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
