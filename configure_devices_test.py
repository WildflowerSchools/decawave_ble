from decawave_ble import configure_devices
from decawave_ble.config.csv import ConfigurationDatabaseCSVLocal
import logging

logging.basicConfig(level=logging.DEBUG)

# Configuration databases
config_database_path = 'config_data/tech_room_config_database.csv'

# Configure from database
logging.info('Configuring from database')
configure_devices.configure_devices_from_database(ConfigurationDatabaseCSVLocal(config_database_path))
