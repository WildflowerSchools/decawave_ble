from decawave_ble import *
import bluepy.btle
import json

# Paths for saving results
output_path_stem = 'scan_results'
text_output_path = output_path_stem + '.txt'
json_output_path = output_path_stem + '.json'

# Scan for Decawave devices
print('\nScanning for Decawave devices')
decawave_scan_entries = get_decawave_scan_entries()
num_decawave_devices = len(decawave_scan_entries)
print('Found {} Decawave devices'.format(num_decawave_devices))

# Get data from Decawave devices
print('\nGetting data from Decawave devices')
decawave_devices = []
anchor_scan_entries = []
tag_scan_entries = []
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
	if operation_mode_data['device_type_name'] == 'Anchor':
		anchor_scan_entries.append(decawave_scan_entry)
	if operation_mode_data['device_type_name'] == 'Tag':
		tag_scan_entries.append(decawave_scan_entry)
	# Get device info data
	print('Getting device info data')
	device_info_data = get_device_info_data(decawave_peripheral)
	# Get network ID
	print('Getting network ID')
	network_id = get_network_id(decawave_peripheral)
	# Get location data mode data
	print('Getting location data mode')
	location_data_mode_data = get_location_data_mode_data(decawave_peripheral)
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
		'location_data_mode_data': location_data_mode_data,
		'location_data': location_data,
		'proxy_positions_data': proxy_positions_data,
		'anchor_list_data': anchor_list_data,
		'update_rate_data': update_rate_data})

# Write results to JSON file
print('\nSaving results in {}'.format(json_output_path))
with open(json_output_path, 'w') as file:
	json.dump(
		decawave_devices, file,
		cls=CustomJSONEncoder,
		indent=2)

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

# Write data to Decawave devices

print('\nWriting data to Decawave devices')
test_anchor_scan_entry = anchor_scan_entries[0]
scan_data = get_scan_data(test_anchor_scan_entry)
device_name = get_device_name(scan_data)

# Connect to Decawave device
print('\nConnecting to Decawave device {}'.format(device_name))
decawave_peripheral = get_decawave_peripheral(test_anchor_scan_entry)

# Get location data
print('\nGetting location data')
location_data_before = get_location_data(decawave_peripheral)
# Print location data
print('Position data:')
print('  X: {} mm'.format(location_data_before['position_data']['x_position']))
print('  Y: {} mm'.format(location_data_before['position_data']['y_position']))
print('  Z: {} mm'.format(location_data_before['position_data']['z_position']))
print('  Quality: {}'.format(location_data_before['position_data']['quality']))

# Write persisted position data
print('\nWriting new persisted position data')
persisted_position_data = {
	'x_position': 100,
	'y_position': 200,
	'z_position': 300,
	'quality': 100}
write_persisted_position_data(decawave_peripheral, persisted_position_data)

# Get location data
print('\nGetting location data')
location_data_after = get_location_data(decawave_peripheral)
# Print location data
print('Position data:')
print('  X: {} mm'.format(location_data_after['position_data']['x_position']))
print('  Y: {} mm'.format(location_data_after['position_data']['y_position']))
print('  Z: {} mm'.format(location_data_after['position_data']['z_position']))
print('  Quality: {}'.format(location_data_after['position_data']['quality']))

# Write persisted position data
print('\nRestoring persisted position data')
persisted_position_data = location_data_before['position_data']
write_persisted_position_data(decawave_peripheral, persisted_position_data)

# Get location data
print('\nGetting location data')
location_data_restored = get_location_data(decawave_peripheral)
# Print location data
print('Position data:')
print('  X: {} mm'.format(location_data_restored['position_data']['x_position']))
print('  Y: {} mm'.format(location_data_restored['position_data']['y_position']))
print('  Z: {} mm'.format(location_data_restored['position_data']['z_position']))
print('  Quality: {}'.format(location_data_restored['position_data']['quality']))

# Get operation mode data
print('\nGetting operation mode data')
operation_mode_data_before = get_operation_mode_data(decawave_peripheral)
# Print location data
print('Operation mode data:')
print('  Device type: {}'.format(operation_mode_data_before['device_type']))
print('  Device type name: {}'.format(operation_mode_data_before['device_type_name']))
print('  UWB mode: {}'.format(operation_mode_data_before['uwb_mode']))
print('  UWB mode name: {}'.format(operation_mode_data_before['uwb_mode_name']))
print('  FW version: {}'.format(operation_mode_data_before['fw_version']))
print('  FW version name: {}'.format(operation_mode_data_before['fw_version_name']))
print('  Accelerometer enable: {}'.format(operation_mode_data_before['accelerometer_enable']))
print('  LED enable: {}'.format(operation_mode_data_before['led_enable']))
print('  FW update enable: {}'.format(operation_mode_data_before['fw_update_enable']))
print('  Reserved (1): {}'.format(operation_mode_data_before['reserved_01']))
print('  Initiator: {}'.format(operation_mode_data_before['initiator']))
print('  Low power mode: {}'.format(operation_mode_data_before['low_power_mode']))
print('  Location engine: {}'.format(operation_mode_data_before['location_engine']))
print('  Reserved (2): {}'.format(operation_mode_data_before['reserved_02']))

# Write new operation mode data
print('\nWriting new operation mode data')
operation_mode_data = {
	'device_type': 0,
	'uwb_mode': 1,
	'fw_version': operation_mode_data_before['fw_version'],
	'accelerometer_enable': operation_mode_data_before['accelerometer_enable'],
	'led_enable': operation_mode_data_before['led_enable'],
	'fw_update_enable': operation_mode_data_before['fw_update_enable'],
	'reserved_01': operation_mode_data_before['reserved_01'],
	'initiator': False,
	'low_power_mode': operation_mode_data_before['low_power_mode'],
	'location_engine': operation_mode_data_before['location_engine'],
	'reserved_02': operation_mode_data_before['location_engine']}
write_operation_mode_data(decawave_peripheral, operation_mode_data)

# Get operation mode data
print('\nGetting operation mode data')
operation_mode_data_after = get_operation_mode_data(decawave_peripheral)
# Print location data
print('Operation mode data:')
print('  Device type: {}'.format(operation_mode_data_after['device_type']))
print('  Device type name: {}'.format(operation_mode_data_after['device_type_name']))
print('  UWB mode: {}'.format(operation_mode_data_after['uwb_mode']))
print('  UWB mode name: {}'.format(operation_mode_data_after['uwb_mode_name']))
print('  FW version: {}'.format(operation_mode_data_after['fw_version']))
print('  FW version name: {}'.format(operation_mode_data_after['fw_version_name']))
print('  Accelerometer enable: {}'.format(operation_mode_data_after['accelerometer_enable']))
print('  LED enable: {}'.format(operation_mode_data_after['led_enable']))
print('  FW update enable: {}'.format(operation_mode_data_after['fw_update_enable']))
print('  Reserved (1): {}'.format(operation_mode_data_after['reserved_01']))
print('  Initiator: {}'.format(operation_mode_data_after['initiator']))
print('  Low power mode: {}'.format(operation_mode_data_after['low_power_mode']))
print('  Location engine: {}'.format(operation_mode_data_after['location_engine']))
print('  Reserved (2): {}'.format(operation_mode_data_after['reserved_02']))

# Restoring operation mode data
print('\nRestoring operation mode data')
write_operation_mode_data(decawave_peripheral, operation_mode_data_before)

# Get operation mode data
print('\nGetting operation mode data')
operation_mode_data_restored = get_operation_mode_data(decawave_peripheral)
# Print location data
print('Operation mode data:')
print('  Device type: {}'.format(operation_mode_data_restored['device_type']))
print('  Device type name: {}'.format(operation_mode_data_restored['device_type_name']))
print('  UWB mode: {}'.format(operation_mode_data_restored['uwb_mode']))
print('  UWB mode name: {}'.format(operation_mode_data_restored['uwb_mode_name']))
print('  FW version: {}'.format(operation_mode_data_restored['fw_version']))
print('  FW version name: {}'.format(operation_mode_data_restored['fw_version_name']))
print('  Accelerometer enable: {}'.format(operation_mode_data_restored['accelerometer_enable']))
print('  LED enable: {}'.format(operation_mode_data_restored['led_enable']))
print('  FW update enable: {}'.format(operation_mode_data_restored['fw_update_enable']))
print('  Reserved (1): {}'.format(operation_mode_data_restored['reserved_01']))
print('  Initiator: {}'.format(operation_mode_data_restored['initiator']))
print('  Low power mode: {}'.format(operation_mode_data_restored['low_power_mode']))
print('  Location engine: {}'.format(operation_mode_data_restored['location_engine']))
print('  Reserved (2): {}'.format(operation_mode_data_restored['reserved_02']))

# Get update rate data
print('\nGetting update rate data')
update_rate_data_before = get_update_rate_data(decawave_peripheral)
# Print location data
print('Update rate data:')
print('  Moving update rate: {}'.format(update_rate_data_before['moving_update_rate']))
print('  Stationary update rate: {}'.format(update_rate_data_before['stationary_update_rate']))

# Write new update rate data
print('\nWriting new update rate data')
update_rate_data = {
	'moving_update_rate': 300,
	'stationary_update_rate': 400}
write_update_rate_data(decawave_peripheral, update_rate_data)

# Get update rate data
print('\nGetting update rate data')
update_rate_data_after = get_update_rate_data(decawave_peripheral)
# Print location data
print('Update rate data:')
print('  Moving update rate: {}'.format(update_rate_data_after['moving_update_rate']))
print('  Stationary update rate: {}'.format(update_rate_data_after['stationary_update_rate']))

# Restore update rate data
print('\nRestoring update rate data')
write_update_rate_data(decawave_peripheral, update_rate_data_before)

# Get update rate data
print('\nGetting update rate data')
update_rate_data_restored = get_update_rate_data(decawave_peripheral)
# Print location data
print('Update rate data:')
print('  Moving update rate: {}'.format(update_rate_data_restored['moving_update_rate']))
print('  Stationary update rate: {}'.format(update_rate_data_restored['stationary_update_rate']))

# Disconnect from device
decawave_peripheral.disconnect()
