import decawave_ble
from decawave_ble import configure_devices
from decawave_ble.config.csv import ConfigurationDatabaseCSVLocal

# Configuration databases
baseline_config_database_path = 'config_data/baseline_config_database.csv'
new_config_database_path = 'config_data/new_config_database.csv'

# Paths for saving results
output_path_stem_before = 'output/before_configuration'
text_output_path_before = output_path_stem_before + '.txt'
json_output_path_before = output_path_stem_before + '.json'
output_path_stem_after = 'output/after_configuration'
text_output_path_after = output_path_stem_after + '.txt'
json_output_path_after = output_path_stem_after + '.json'
output_path_stem_restored = 'output/restored'
text_output_path_restored = output_path_stem_restored + '.txt'
json_output_path_restored = output_path_stem_restored + '.json'

# Scan for Decawave devices
print('\nScanning for Decawave devices')
decawave_devices = decawave_ble.scan_for_decawave_devices()
num_decawave_devices = len(decawave_devices)
print('Found {} Decawave devices'.format(num_decawave_devices))

# Get data from Decawave devices and write files
print('\nGetting data from Decawave devices (before configuration)')
decawave_device_data_before = decawave_ble.get_data_multiple_devices(decawave_devices)
decawave_ble.write_data_multiple_devices_to_json_local(
    decawave_device_data_before,
    json_output_path_before)
decawave_ble.write_data_multiple_devices_to_text_local(
    decawave_device_data_before,
    text_output_path_before)

# Configure from database
print('\nConfiguring from database')
configure_devices.configure_devices_from_database(ConfigurationDatabaseCSVLocal(new_config_database_path))

# Get data from Decawave devices and write files
print('\nGetting data from Decawave devices (after new configuration)')
decawave_device_data_after = decawave_ble.get_data_multiple_devices(decawave_devices)
decawave_ble.write_data_multiple_devices_to_json_local(
    decawave_device_data_after,
    json_output_path_after)
decawave_ble.write_data_multiple_devices_to_text_local(
    decawave_device_data_after,
    text_output_path_after)

# Restore baseline from database
print('\nRestoring baseline from database')
configure_devices.configure_devices_from_database(ConfigurationDatabaseCSVLocal(baseline_config_database_path))

# Get data from Decawave devices and write files
print('\nGetting data from Decawave devices (after restoration)')
decawave_device_data_restored = decawave_ble.get_data_multiple_devices(decawave_devices)
decawave_ble.write_data_multiple_devices_to_json_local(
    decawave_device_data_restored,
    json_output_path_restored)
decawave_ble.write_data_multiple_devices_to_text_local(
    decawave_device_data_restored,
    text_output_path_restored)
