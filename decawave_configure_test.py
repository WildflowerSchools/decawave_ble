from decawave_ble import *
import configure_devices
import json

# Paths for saving results
output_path_stem_before = 'before_configuration'
text_output_path_before = output_path_stem_before + '.txt'
json_output_path_before = output_path_stem_before + '.json'
output_path_stem_after = 'after_configuration'
text_output_path_after = output_path_stem_after + '.txt'
json_output_path_after = output_path_stem_after + '.json'
output_path_stem_restored = 'restored'
text_output_path_restored = output_path_stem_restored + '.txt'
json_output_path_restored = output_path_stem_restored + '.json'

# Scan for Decawave devices
print('\nScanning for Decawave devices')
decawave_devices = scan_for_decawave_devices()
num_decawave_devices = len(decawave_devices)
print('Found {} Decawave devices'.format(num_decawave_devices))

# Get data from Decawave devices
print('\nGetting data from Decawave devices (before configuration)')
decawave_device_data_before = {}
for device_name, decawave_device in decawave_devices.items():
	print('\nGetting data for {}'.format(device_name))
	data = get_data(decawave_device)
	decawave_device_data_before[device_name] = data

# Write results to JSON file
print('\nSaving results in {}'.format(json_output_path_before))
with open(json_output_path_before, 'w') as file:
	json.dump(
		decawave_device_data_before,
		file,
		cls=CustomJSONEncoder,
		indent=2)

# Write results to text file
print('Saving results in {}'.format(text_output_path_before))
with open(text_output_path_before, 'w') as file:
	file.write('{} Decawave devices found:\n'.format(num_decawave_devices))
	for device_name, decawave_device in decawave_device_data_before.items():
		file.write('\nDevice name: {}\n'.format(device_name))
		file.write('RSSI: {} dB\n'.format(decawave_device['scan_data']['rssi']))
		file.write('Device type: {}\n'.format(decawave_device['operation_mode_data']['device_type_name']))
		file.write('Initiator: {}\n'.format(decawave_device['operation_mode_data']['initiator']))
		file.write('UWB mode: {}\n'.format(decawave_device['operation_mode_data']['uwb_mode_name']))
		file.write('Network ID: {}\n'.format(decawave_device['network_id']))
		file.write('Node ID: {:08X}\n'.format(decawave_device['device_info_data']['node_id']))
		file.write('Bridge: {}\n'.format(decawave_device['device_info_data']['bridge']))
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
		if decawave_device['anchor_list_data'] is not None:
			file.write('Anchor list data:\n')
			for node_id in decawave_device['anchor_list_data']:
				file.write('  Node ID: {:04X}\n'.format(node_id))
		if decawave_device['update_rate_data'] is not None:
			file.write('Moving update rate (ms): {}\n'.format(decawave_device['update_rate_data']['moving_update_rate']))
			file.write('Stationary update rate (ms): {}\n'.format(decawave_device['update_rate_data']['stationary_update_rate']))

# Configure from database

print('\nConfiguring from database')
configure_devices.configure_devices_from_database('test_config_database.csv')

# Get data from Decawave devices
print('\nGetting data from Decawave devices (after configuration)')
decawave_device_data_after = {}
for device_name, decawave_device in decawave_devices.items():
	print('\nGetting data for {}'.format(device_name))
	data = get_data(decawave_device)
	decawave_device_data_after[device_name] = data

# Write results to JSON file
print('\nSaving results in {}'.format(json_output_path_after))
with open(json_output_path_after, 'w') as file:
	json.dump(
		decawave_device_data_after,
		file,
		cls=CustomJSONEncoder,
		indent=2)

# Write results to text file
print('Saving results in {}'.format(text_output_path_after))
with open(text_output_path_after, 'w') as file:
	file.write('{} Decawave devices found:\n'.format(num_decawave_devices))
	for device_name, decawave_device in decawave_device_data_after.items():
		file.write('\nDevice name: {}\n'.format(device_name))
		file.write('RSSI: {} dB\n'.format(decawave_device['scan_data']['rssi']))
		file.write('Device type: {}\n'.format(decawave_device['operation_mode_data']['device_type_name']))
		file.write('Initiator: {}\n'.format(decawave_device['operation_mode_data']['initiator']))
		file.write('UWB mode: {}\n'.format(decawave_device['operation_mode_data']['uwb_mode_name']))
		file.write('Network ID: {}\n'.format(decawave_device['network_id']))
		file.write('Node ID: {:08X}\n'.format(decawave_device['device_info_data']['node_id']))
		file.write('Bridge: {}\n'.format(decawave_device['device_info_data']['bridge']))
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
		if decawave_device['anchor_list_data'] is not None:
			file.write('Anchor list data:\n')
			for node_id in decawave_device['anchor_list_data']:
				file.write('  Node ID: {:04X}\n'.format(node_id))
		if decawave_device['update_rate_data'] is not None:
			file.write('Moving update rate (ms): {}\n'.format(decawave_device['update_rate_data']['moving_update_rate']))
			file.write('Stationary update rate (ms): {}\n'.format(decawave_device['update_rate_data']['stationary_update_rate']))

# Restore baseline from database

print('\nRestoring baseline from database')
configure_devices.configure_devices_from_database('baseline_config_database.csv')

# Get data from Decawave devices
print('\nGetting data from Decawave devices (restored)')
decawave_device_data_restored = {}
for device_name, decawave_device in decawave_devices.items():
	print('\nGetting data for {}'.format(device_name))
	data = get_data(decawave_device)
	decawave_device_data_restored[device_name] = data

# Write results to JSON file
print('\nSaving results in {}'.format(json_output_path_restored))
with open(json_output_path_restored, 'w') as file:
	json.dump(
		decawave_device_data_restored,
		file,
		cls=CustomJSONEncoder,
		indent=2)

# Write results to text file
print('Saving results in {}'.format(text_output_path_restored))
with open(text_output_path_restored, 'w') as file:
	file.write('{} Decawave devices found:\n'.format(num_decawave_devices))
	for device_name, decawave_device in decawave_device_data_restored.items():
		file.write('\nDevice name: {}\n'.format(device_name))
		file.write('RSSI: {} dB\n'.format(decawave_device['scan_data']['rssi']))
		file.write('Device type: {}\n'.format(decawave_device['operation_mode_data']['device_type_name']))
		file.write('Initiator: {}\n'.format(decawave_device['operation_mode_data']['initiator']))
		file.write('UWB mode: {}\n'.format(decawave_device['operation_mode_data']['uwb_mode_name']))
		file.write('Network ID: {}\n'.format(decawave_device['network_id']))
		file.write('Node ID: {:08X}\n'.format(decawave_device['device_info_data']['node_id']))
		file.write('Bridge: {}\n'.format(decawave_device['device_info_data']['bridge']))
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
		if decawave_device['anchor_list_data'] is not None:
			file.write('Anchor list data:\n')
			for node_id in decawave_device['anchor_list_data']:
				file.write('  Node ID: {:04X}\n'.format(node_id))
		if decawave_device['update_rate_data'] is not None:
			file.write('Moving update rate (ms): {}\n'.format(decawave_device['update_rate_data']['moving_update_rate']))
			file.write('Stationary update rate (ms): {}\n'.format(decawave_device['update_rate_data']['stationary_update_rate']))

