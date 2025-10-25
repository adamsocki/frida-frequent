import modules.frida as Frida
import urllib.request
import json
import os
from dotenv import load_dotenv
import ssl
import certifi

# Load environment variables from .env file
load_dotenv()


class TransitManager():
    def __init__(self):
        Frida.logger.info("Create Transit Manager.")
        self.api_key = os.getenv('WMATA_API_KEY')
        if not self.api_key:
            Frida.logger.error("WMATA_API_KEY not found in environment variables!")


    def init_transit_manager(self):
        Frida.logger.info("Initializing Transit Manager...")

    def _fetch_wmata_data(self) -> dict:
        """Fetch predictions from WMATA API."""
        try:
            Frida.logger.info("Fetching transit arrivals from WMATA API...")
            
            api_key = os.getenv('WMATA_API_KEY')
            if not api_key:
                raise ValueError("WMATA_API_KEY not found in environment variables")
            
            url = f"{self.api_url}?StopID={self.stop_id}"
            
            headers = {
                'Cache-Control': 'no-cache',
                'api_key': api_key,
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            # Create SSL context with certifi certificates
            context = ssl.create_default_context(cafile=certifi.where())
            
            response = urllib.request.urlopen(req, context=context)
            
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                Frida.logger.info(f"Successfully fetched WMATA data: {len(data.get('Predictions', []))} predictions")
                Frida.logger.debug(f"Raw API response: {json.dumps(data, indent=2)}")
                return data
            else:
                Frida.logger.error(f"WMATA API returned status code: {response.getcode()}")
                return {}
        except Exception as e:
            Frida.logger.error(f"Error fetching WMATA data: {e}")
            return {}

    def get_arrivals(self):
        """Fetch and parse transit arrivals."""
        if not self.api_key:
            Frida.logger.error("API key not configured")
            return []

        try:
            # Get configuration
            api_url = Frida.config['transit']['api_url']
            stop_id = Frida.config['transit']['stop_id']
            
            self.stop_id = stop_id
            self.api_url = api_url
            
            # Fetch data
            data = self._fetch_wmata_data()
            
            # Transform WMATA data to internal format
            arrivals = []
            if 'Predictions' in data:
                Frida.logger.info(f"Parsing {len(data['Predictions'])} predictions from WMATA API")
                for prediction in data['Predictions']:
                    arrival = {
                        "route": prediction.get('RouteID', 'N/A'),
                        "headsign": prediction.get('DirectionText', 'N/A'),
                        "arrival_in_min": prediction.get('Minutes', 0),
                    }
                    arrivals.append(arrival)
                    
                    # Log each arrival with details
                    Frida.logger.info(
                        f"  Route {arrival['route']}: {arrival['headsign']} - "
                        f"arriving in {arrival['arrival_in_min']} min"
                    )
            else:
                Frida.logger.warning("No 'Predictions' key found in API response")
            
            Frida.logger.info(f"Successfully parsed {len(arrivals)} arrivals")
            return arrivals
            
        except urllib.error.HTTPError as e:
            Frida.logger.error(f"HTTP Error fetching WMATA data: {e.code} - {e.reason}")
            return []
        except urllib.error.URLError as e:
            Frida.logger.error(f"URL Error fetching WMATA data: {e.reason}")
            return []
        except json.JSONDecodeError as e:
            Frida.logger.error(f"JSON parsing error: {e}")
            return []
        except Exception as e:
            Frida.logger.error(f"Unexpected error fetching WMATA data: {e}")
            return []


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