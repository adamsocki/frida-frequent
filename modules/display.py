import modules.frida as Frida


class DisplayManager:

    def __init__(self):
        """Create DisplayManager (doesn't initialize hardware yet)"""
        self.model = None
        self.rotation = None
        self.epd = None


    def init_display_manager(self, model: str, rotation: int = 0) -> bool:
        """Initialize the actual hardware"""
        self.model = model
        self.rotation = rotation

        # Skip hardware initialization in development mode
        if Frida.DEVELOPMENT_MODE:
            Frida.logger.info(f"Running in DEVELOPMENT MODE - Display - {model} will be stubbed")
            return True

        try:
            self.epd = self._init_waveshare(model)
            if self.epd is None:
                Frida.logger.error("Failed to initialize epd module")
                return False

            Frida.logger.info(f"Display hardware initialized: {model}")
            return True
        except Exception as e:
            Frida.logger.error(f"Display initialization error: {e}")
            return False


    def display_loop(self):
        while not Frida.shutdown_event.is_set():
            if Frida.display_manager:
                # Frida.logger.info("Display Manager is running.")
                pass

    def _init_waveshare(self, model: str):
        """Initialize Waveshare e-paper display"""
        # TODO: Import and initialize actual waveshare library
        # from waveshare_epd import epd2in13_V4
        # epd = epd2in13_V4.EPD()
        # epd.init()
        # return epd
        return None