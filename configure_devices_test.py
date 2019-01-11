import decawave_ble
import configure_devices

# Configuration databases
config_database_path = 'config_data/tech_room_config_database.csv'

# Configure from database
print('\nConfiguring from database')
configure_devices.configure_devices_from_database(config_database_path)


