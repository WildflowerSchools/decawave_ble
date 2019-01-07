from decawave_ble import *
import bluepy.btle
import json

# Extend the default JSON encoder so it can handle bluepy.btle.UUID objects
class CustomJSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, bluepy.btle.UUID):
			return str(obj)
		return json.JSONencoder.default(self.obj)

# Paths for saving results
output_path_stem = 'scan_results'
text_output_path = output_path_stem + '.txt'
json_output_path = output_path_stem + '.json'

# Scan for Decawave devices
decawave_scan_entries = get_decawave_scan_entries()
num_decawave_devices = len(decawave_scan_entries)
print('\nFound {} Decawave devices'.format(num_decawave_devices))

# Get data from Decawave devices
print('\nGetting data from Decawave devices')
decawave_devices = []
for decawave_scan_entry in decawave_scan_entries:
	# Get scan data
	print('\nGetting scan data')
	scan_data = get_scan_data(decawave_scan_entry)
	device_name = get_device_name(scan_data)
	# Connect to Decawave device
	print('Connecting to Decawave device {}'.format(device_name))
	decawave_peripheral = get_decawave_peripheral(decawave_scan_entry)
	# Get operation mode data
	print('Getting operation mode data')
	operation_mode_data = get_operation_mode_data(decawave_peripheral)
	# Get operation mode data
	print('Getting device info data')
	device_info_data = get_device_info_data(decawave_peripheral)
	# Get network ID
	print('Getting network ID')
	network_id = get_network_id(decawave_peripheral)
	# Get location data mode data
	print('Getting location data mode')
	location_data_mode = get_location_data_mode(decawave_peripheral)
	# Get location data
	print('Getting location data')
	location_data = get_location_data(decawave_peripheral)
	# Get proxy positions data
	print('Getting proxy positions data')
	proxy_positions_data = get_proxy_positions_data(decawave_peripheral)
	print('Device type: {}'.format(operation_mode_data['device_type_name']))
	# Get anchor list data
	if operation_mode_data['device_type_name'] == 'Anchor':
		print('Getting anchor list data')
		anchor_list_data = get_anchor_list_data(decawave_peripheral)
	else:
		anchor_list_data = None
	# Get anchor list data
	if operation_mode_data['device_type_name'] == 'Tag':
		print('Getting update rate data')
		update_rate_data = get_update_rate_data(decawave_peripheral)
	else:
		update_rate_data = None
	# Disconnect from device
	decawave_peripheral.disconnect()
	# Populate device data
	decawave_devices.append({
		'device_name': device_name,
		'scan_data': scan_data,
		'operation_mode_data': operation_mode_data,
		'device_info_data': device_info_data,
		'network_id': network_id,
		'location_data_mode': location_data_mode,
		'location_data': location_data,
		'proxy_positions_data': proxy_positions_data,
		'anchor_list_data': anchor_list_data,
		'update_rate_data': update_rate_data})

# Write results to JSON file
print('Saving results in {}'.format(json_output_path))
with open(json_output_path, 'w') as file:
	json.dump(decawave_devices, file, cls=CustomJSONEncoder)

# Write results to text file
print('Saving results in {}'.format(text_output_path))
with open(text_output_path, 'w') as file:
	file.write('{} Decawave devices found:\n'.format(num_decawave_devices))
	for decawave_device in decawave_devices:
		file.write('\nDevice name: {}\n'.format(decawave_device['device_name']))
		file.write('RSSI: {} dB\n'.format(decawave_device['scan_data']['rssi']))
		file.write('Device type: {}\n'.format(decawave_device['operation_mode_data']['device_type_name']))
		file.write('Initiator: {}\n'.format(decawave_device['operation_mode_data']['initiator']))
		file.write('UWB mode: {}\n'.format(decawave_device['operation_mode_data']['uwb_mode_name']))
		file.write('Network ID: {}\n'.format(decawave_device['network_id']))
		file.write('Node ID: {:08X}\n'.format(decawave_device['device_info_data']['node_id']))
		file.write('Bridge: {}\n'.format(decawave_device['device_info_data']['bridge']))
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
