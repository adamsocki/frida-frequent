import modules.frida as Frida


class TransitManager():
    def __init__(self):
        Frida.logger.info("Create Transit Manager.")


    def init_transit_manager(self):
        Frida.logger.info("Initializing Transit Manager...")

    def get_arrivals(self):
        Frida.logger.info("Fetching transit arrivals from API...")

        # Simulate API call - replace with real API interaction
        arrivals = [
            {"route": "Bus 42", "arrival_in_min": 5},
            {"route": "Train A", "arrival_in_min": 12},
        ]

        return arrivals


    def fetch_loop(self):
        
        Frida.logger.info("Starting Transit Manager fetch loop...")

        interval = Frida.config['transit']['refresh_interval']

        while not Frida.shutdown_event.is_set():
            try:
                if Frida.transit_manager:
                    arrivals = Frida.transit_manager.get_arrivals()

                    with Frida.data_lock:
                        transit_data = arrivals

                    Frida.logger.info(f"Fetched {len(arrivals)} arrivals")
                else:
                    Frida.logger.warning("Transit manager not available")

            except Exception as e:
                Frida.logger.warning(f"Failed to fetch transit data: {e}")
            # Keep old data, retry on next interval

            # Sleep but wake up if shutdown requested
            Frida.shutdown_event.wait(timeout=interval)