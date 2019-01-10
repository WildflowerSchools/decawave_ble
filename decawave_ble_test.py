from decawave_ble import *
import bluepy.btle
import json

# Paths for saving results
output_path_stem = 'scan_results'
text_output_path = output_path_stem + '.txt'
json_output_path = output_path_stem + '.json'

# Scan for Decawave devices
print('\nScanning for Decawave devices')
decawave_devices = scan_for_decawave_devices()
num_decawave_devices = len(decawave_devices)
print('Found {} Decawave devices'.format(num_decawave_devices))

# Get data from Decawave devices
print('\nGetting data from Decawave devices')
decawave_device_data = {}
for device_name, decawave_device in decawave_devices.items():
	print('\nGetting data for {}'.format(device_name))
	data = get_data(decawave_device)
	decawave_device_data[device_name] = data

# Write results to JSON file
print('\nSaving results in {}'.format(json_output_path))
with open(json_output_path, 'w') as file:
	json.dump(
		decawave_device_data,
		file,
		cls=CustomJSONEncoder,
		indent=2)

# Write results to text file
print('Saving results in {}'.format(text_output_path))
with open(text_output_path, 'w') as file:
	file.write('{} Decawave devices found:\n'.format(num_decawave_devices))
	for device_name, decawave_device in decawave_device_data.items():
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

# Write data to Decawave device
print('\nWriting data to Decawave device')
for device_name, data in decawave_device_data.items():
	if data['operation_mode_data']['device_type_name'] == 'Anchor':
		decawave_device = decawave_devices[device_name]
		original_data = data
		break
print('Chosen device: {}'.format(decawave_device.device_name))

# Print location data (before)
print('\nPosition data (before change):')
print('  X: {} mm'.format(original_data['location_data']['position_data']['x_position']))
print('  Y: {} mm'.format(original_data['location_data']['position_data']['y_position']))
print('  Z: {} mm'.format(original_data['location_data']['position_data']['z_position']))
print('  Quality: {}'.format(original_data['location_data']['position_data']['quality']))

# Print operation mode data (before)
print('Operation mode data (before change):')
print('  Device type: {}'.format(original_data['operation_mode_data']['device_type']))
print('  Device type name: {}'.format(original_data['operation_mode_data']['device_type_name']))
print('  UWB mode: {}'.format(original_data['operation_mode_data']['uwb_mode']))
print('  UWB mode name: {}'.format(original_data['operation_mode_data']['uwb_mode_name']))
print('  FW version: {}'.format(original_data['operation_mode_data']['fw_version']))
print('  FW version name: {}'.format(original_data['operation_mode_data']['fw_version_name']))
print('  Accelerometer enable: {}'.format(original_data['operation_mode_data']['accelerometer_enable']))
print('  LED enable: {}'.format(original_data['operation_mode_data']['led_enable']))
print('  FW update enable: {}'.format(original_data['operation_mode_data']['fw_update_enable']))
print('  Reserved (1): {}'.format(original_data['operation_mode_data']['reserved_01']))
print('  Initiator: {}'.format(original_data['operation_mode_data']['initiator']))
print('  Low power mode: {}'.format(original_data['operation_mode_data']['low_power_mode']))
print('  Location engine: {}'.format(original_data['operation_mode_data']['location_engine']))
print('  Reserved (2): {}'.format(original_data['operation_mode_data']['reserved_02']))

# Print update rate data (before)
print('Update rate data (before change):')
print('  Moving update rate: {}'.format(original_data['update_rate_data']['moving_update_rate']))
print('  Stationary update rate: {}'.format(original_data['update_rate_data']['stationary_update_rate']))

# Write new data
print('\nWriting new data')
set_config(
	decawave_device,
	x_position = 100,
	y_position = 200,
	z_position = 300,
	device_type_name = 'Tag',
	uwb_mode_name = 'Passive',
	initiator = False,
	moving_update_rate = 300,
	stationary_update_rate = 400)

# Get new data
print('\nGetting new data')
new_data = get_data(decawave_device)

# Print location data (after)
print('\nPosition data (new):')
print('  X: {} mm'.format(new_data['location_data']['position_data']['x_position']))
print('  Y: {} mm'.format(new_data['location_data']['position_data']['y_position']))
print('  Z: {} mm'.format(new_data['location_data']['position_data']['z_position']))
print('  Quality: {}'.format(new_data['location_data']['position_data']['quality']))

# Print operation_mode data (after)
print('Operation mode data (new):')
print('  Device type: {}'.format(new_data['operation_mode_data']['device_type']))
print('  Device type name: {}'.format(new_data['operation_mode_data']['device_type_name']))
print('  UWB mode: {}'.format(new_data['operation_mode_data']['uwb_mode']))
print('  UWB mode name: {}'.format(new_data['operation_mode_data']['uwb_mode_name']))
print('  FW version: {}'.format(new_data['operation_mode_data']['fw_version']))
print('  FW version name: {}'.format(new_data['operation_mode_data']['fw_version_name']))
print('  Accelerometer enable: {}'.format(new_data['operation_mode_data']['accelerometer_enable']))
print('  LED enable: {}'.format(new_data['operation_mode_data']['led_enable']))
print('  FW update enable: {}'.format(new_data['operation_mode_data']['fw_update_enable']))
print('  Reserved (1): {}'.format(new_data['operation_mode_data']['reserved_01']))
print('  Initiator: {}'.format(new_data['operation_mode_data']['initiator']))
print('  Low power mode: {}'.format(new_data['operation_mode_data']['low_power_mode']))
print('  Location engine: {}'.format(new_data['operation_mode_data']['location_engine']))
print('  Reserved (2): {}'.format(new_data['operation_mode_data']['reserved_02']))

# Print update rate data (after)
print('Update rate data (new):')
print('  Moving update rate: {}'.format(new_data['update_rate_data']['moving_update_rate']))
print('  Stationary update rate: {}'.format(new_data['update_rate_data']['stationary_update_rate']))

# Restoring data
print('\nRestoring data')
restoring_data = {
	'persisted_position_data': original_data['location_data']['position_data'],
	'operation_mode_data': original_data['operation_mode_data'],
	'update_rate_data': original_data['update_rate_data']}
write_data(
	decawave_device,
	restoring_data)

# Get restored data
print('\nGetting restored data')
restored_data = get_data(decawave_device)

# Print location data (restored)
print('\nPosition data (restored):')
print('  X: {} mm'.format(restored_data['location_data']['position_data']['x_position']))
print('  Y: {} mm'.format(restored_data['location_data']['position_data']['y_position']))
print('  Z: {} mm'.format(restored_data['location_data']['position_data']['z_position']))
print('  Quality: {}'.format(restored_data['location_data']['position_data']['quality']))

# Print operation mode data (restored)
print('Operation mode data (restored):')
print('  Device type: {}'.format(restored_data['operation_mode_data']['device_type']))
print('  Device type name: {}'.format(restored_data['operation_mode_data']['device_type_name']))
print('  UWB mode: {}'.format(restored_data['operation_mode_data']['uwb_mode']))
print('  UWB mode name: {}'.format(restored_data['operation_mode_data']['uwb_mode_name']))
print('  FW version: {}'.format(restored_data['operation_mode_data']['fw_version']))
print('  FW version name: {}'.format(restored_data['operation_mode_data']['fw_version_name']))
print('  Accelerometer enable: {}'.format(restored_data['operation_mode_data']['accelerometer_enable']))
print('  LED enable: {}'.format(restored_data['operation_mode_data']['led_enable']))
print('  FW update enable: {}'.format(restored_data['operation_mode_data']['fw_update_enable']))
print('  Reserved (1): {}'.format(restored_data['operation_mode_data']['reserved_01']))
print('  Initiator: {}'.format(restored_data['operation_mode_data']['initiator']))
print('  Low power mode: {}'.format(restored_data['operation_mode_data']['low_power_mode']))
print('  Location engine: {}'.format(restored_data['operation_mode_data']['location_engine']))
print('  Reserved (2): {}'.format(restored_data['operation_mode_data']['reserved_02']))

# Print update rate data (restored)
print('Update rate data (restored):')
print('  Moving update rate: {}'.format(restored_data['update_rate_data']['moving_update_rate']))
print('  Stationary update rate: {}'.format(restored_data['update_rate_data']['stationary_update_rate']))
