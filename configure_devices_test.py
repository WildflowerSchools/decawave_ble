from decawave_ble import *
import configure_devices
import json

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

# Function for getting data from multiple Decawave devices
def get_data_multiple_devices(decawave_devices):
	print('\nGetting data from Decawave devices')
	data_multiple = {}
	for device_name, decawave_device in decawave_devices.items():
		print('\nGetting data for {}'.format(device_name))
		data = get_data(decawave_device)
		data_multiple[device_name] = data
	return data_multiple

# Fuction for writing data from multiple Decawave devices to JSON file
def write_data_multiple_devices_to_json_local(data_multiple, path):
	print('\nSaving results in {}'.format(path))
	with open(path, 'w') as file:
		json.dump(
			data_multiple,
			file,
			cls=CustomJSONEncoder,
			indent=2)

# Function for writing data from multiple Decawave devices to text file
def write_data_multiple_devices_to_text_local(data_multiple, path):
	print('Saving results in {}'.format(path))
	with open(path, 'w') as file:
		file.write('Data for {} Decawave devices\n'.format(len(data_multiple)))
		for device_name, decawave_device in data_multiple.items():
			file.write('\nDevice name: {}\n'.format(device_name))
			file.write('Node ID: {:08X}\n'.format(decawave_device['device_info_data']['node_id']))
			file.write('Device type: {}\n'.format(decawave_device['operation_mode_data']['device_type_name']))
			file.write('Initiator: {}\n'.format(decawave_device['operation_mode_data']['initiator']))
			file.write('UWB mode: {}\n'.format(decawave_device['operation_mode_data']['uwb_mode_name']))
			if decawave_device['update_rate_data'] is not None:
				file.write('Moving update rate (ms): {}\n'.format(decawave_device['update_rate_data']['moving_update_rate']))
				file.write('Stationary update rate (ms): {}\n'.format(decawave_device['update_rate_data']['stationary_update_rate']))
			file.write('Location engine: {}\n'.format(decawave_device['operation_mode_data']['location_engine']))
			file.write('Location data mode name: {}\n'.format(decawave_device['location_data_mode_data']['location_data_mode_name']))
			file.write('Location data content name: {}\n'.format(decawave_device['location_data']['location_data_content_name']))
			if decawave_device['location_data']['position_data'] is not None:
				file.write('Position data:\n')
				file.write('  X: {} mm\n'.format(decawave_device['location_data']['position_data']['x_position']))
				file.write('  Y: {} mm\n'.format(decawave_device['location_data']['position_data']['y_position']))
				file.write('  Z: {} mm\n'.format(decawave_device['location_data']['position_data']['z_position']))
				file.write('  Quality: {}\n'.format(decawave_device['location_data']['position_data']['quality']))
			if decawave_device['location_data']['distance_data'] is not None:
				file.write('Distance data:\n')
				for distance_datum in decawave_device['location_data']['distance_data']:
					file.write('  {:04X}: {} mm (Q={})\n'.format(
						distance_datum['node_id'],
						distance_datum['distance'],
						distance_datum['quality']))
			if decawave_device['proxy_positions_data'] is not None:
				file.write('Proxy positions data:\n')
				for proxy_positions_datum in decawave_device['proxy_positions_data']:
					file.write('  Node ID: {:04X}\n'.format(proxy_positions_datum['node_id']))
					file.write('    X: {} mm\n'.format(proxy_positions_datum['x_position']))
					file.write('    Y: {} mm\n'.format(proxy_positions_datum['y_position']))
					file.write('    Z: {} mm\n'.format(proxy_positions_datum['z_position']))
					file.write('    Quality: {}\n'.format(proxy_positions_datum['quality']))

# Scan for Decawave devices
print('\nScanning for Decawave devices')
decawave_devices = scan_for_decawave_devices()
num_decawave_devices = len(decawave_devices)
print('Found {} Decawave devices'.format(num_decawave_devices))

# Get data from Decawave devices and write files
print('\nGetting data from Decawave devices (before configuration)')
decawave_device_data_before = get_data_multiple_devices(decawave_devices)
write_data_multiple_devices_to_json_local(
	decawave_device_data_before,
	json_output_path_before)
write_data_multiple_devices_to_text_local(
	decawave_device_data_before,
	text_output_path_before)

# Configure from database
print('\nConfiguring from database')
configure_devices.configure_devices_from_database(new_config_database_path)

# Get data from Decawave devices and write files
print('\nGetting data from Decawave devices (after new configuration)')
decawave_device_data_after = get_data_multiple_devices(decawave_devices)
write_data_multiple_devices_to_json_local(
	decawave_device_data_after,
	json_output_path_after)
write_data_multiple_devices_to_text_local(
	decawave_device_data_after,
	text_output_path_after)

# Restore baseline from database
print('\nRestoring baseline from database')
configure_devices.configure_devices_from_database(baseline_config_database_path)

# Get data from Decawave devices and write files
print('\nGetting data from Decawave devices (after restoration)')
decawave_device_data_restored = get_data_multiple_devices(decawave_devices)
write_data_multiple_devices_to_json_local(
	decawave_device_data_restored,
	json_output_path_restored)
write_data_multiple_devices_to_text_local(
	decawave_device_data_restored,
	text_output_path_restored)

