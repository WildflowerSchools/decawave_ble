import bluepy.btle
import json
import collections
import bitstruct

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

# BLE advertising data type codes
SHORT_LOCAL_NAME_TYPE_CODE = 8

# Function for identifying Decawave devices from advertising data
def is_decawave_scan_entry(scan_entry):
	short_local_name = scan_entry.getValueText(SHORT_LOCAL_NAME_TYPE_CODE)
	return (short_local_name is not None and short_local_name.startswith('DW'))

# Known Decawave services (from documentation)
NETWORK_NODE_SERVICE_UUID = '680c21d9-c946-4c1f-9c11-baa1c21329e7'

# Uknown Decawave services (found in scan)
UNKNOWN_01_SERVICE_UUID = '00001801-0000-1000-8000-00805f9b34fb'
UNKNOWN_02_SERVICE_UUID = '00001800-0000-1000-8000-00805f9b34fb'

# Known Decawave characteristics for network node service (from documentation)
OPERATION_MODE_CHARACTERISTIC_UUID = '3f0afd88-7770-46b0-b5e7-9fc099598964'
NETWORK_ID_CHARACTERISTIC_UUID = '80f9d8bc-3bff-45bb-a181-2d6a37991208'
LOCATION_DATA_MODE_CHARACTERISTIC_UUID = 'a02b947e-df97-4516-996a-1882521e0ead'
LOCATION_DATA_CHARACTERISTIC_UUID = '003bbdf2-c634-4b3d-ab56-7ec889b89a37'
PROXY_POSITION_CHARACTERISTIC_UUID = 'f4a67d7d-379d-4183-9c03-4b6ea5103291'
DEVICE_INFO_CHARACTERISTIC_UUID = '1e63b1eb-d4ed-444e-af54-c1e965192501'
STATISTICS_CHARACTERISTIC_UUID = '0eb2bc59-baf1-4c1c-8535-8a0204c69de5'
FW_UPDATE_PUSH_CHARACTERISTIC_UUID = '5955aa10-e085-4030-8aa6-bdfac89ac32b'
FW_UPDATE_POLL_CHARACTERISIC_UUID = '9eed0e27-09c0-4d1c-bd92-7c441daba850'
DISCONNECT_CHARACTERISTIC_UUID = 'ed83b848-da03-4a0a-a2dc-8b401080e473'
ANCHOR_PERSISTED_POSITION_CHARACTERISTIC_UUID = 'f0f26c9b-2c8c-49ac-ab60-fe03def1b40c'
ANCHOR_CLUSTER_INFO_CHARACTERISTIC_UUID = '17b1613e-98f2-4436-bcde-23af17a10c72'
ANCHOR_MAC_STATS_CHARACTERISTIC_UUID = '28d01d60-89de-4bfa-b6e9-651ba596232c'
ANCHOR_LIST_CHARACTERISTIC_UUID = '5b10c428-af2f-486f-aee1-9dbd79b6bccb'
TAG_UPDATE_RATE_CHARACTERISTIC_UUID = '7bd47f30-5602-4389-b069-8305731308b6'

# Data and functions for parsing network node service characteristics
# (from documentation)

# Function for parsing bytes from operation mode characteristic
def parse_operation_mode_bytes(operation_mode_bytes):
	operation_mode_data = bitstruct.unpack_dict(
		'u1u2u1b1b1b1b1b1b1b1u4',
		[
			'device_type',
			'uwb_mode',
			'fw_version',
			'accelerometer_enable',
			'led_enable',
			'fw_update_enable',
			'reserved_01',
			'initiator',
			'low_power_mode',
			'location_engine',
			'reserved_02'],
		operation_mode_bytes)
	return operation_mode_data

# Names of operation mode data values
DEVICE_TYPE_NAMES = ['Tag', 'Anchor']
UWB_MODE_NAMES = ['Off', 'Passive', 'Active']
FW_VERSION_NAMES = ['1', '2']

# Function for parsing bytes from location data mode characteristic
def parse_location_data_mode_bytes(location_data_mode_bytes):
	location_data_mode = location_data_mode_bytes[0]
	return location_data_mode

# Names of location data mode data values
LOCATION_DATA_MODE_NAMES = [
	'Position',
	'Distances',
	'Position and distances']

# Function for parsing bytes from location data characteristic
def parse_location_data_bytes(location_data_bytes):
	if len(location_data_bytes) > 0:
		location_data_content = location_data_bytes[0]
		location_data_bytes = location_data_bytes[1:]
	else:
		location_data_content = None
	if (location_data_content == 0 or location_data_content == 2):
		position_bytes = location_data_bytes[:13]
		loction_data_bytes = location_data_bytes[13:]
		position_data = bitstruct.unpack_dict(
			's32s32s32u8<',
			['x_position', 'y_position', 'z_position', 'quality'],
			position_bytes)
	else:
		position_data = None
	if (location_data_content == 1 or location_data_content == 2):
		distance_count = location_data_bytes[0]
		location_data_bytes = location_data_bytes[1:]
		distance_data=[]
		for distance_data_index in range(distance_count):
			distance_datum_bytes = location_data_bytes[:7]
			location_data_bytes = location_data_bytes[7:]
			distance_datum = bitstruct.unpack_dict(
				'u16u32u8<',
				['node_id', 'distance', 'quality'],
				distance_datum_bytes)
			distance_data.append(distance_datum)
	else:
		distance_data = None
	return {
		'position_data': position_data,
		'distance_data': distance_data}

# Function for parsing bytes from network ID characteristic
def parse_network_id_bytes(network_id_bytes):
	network_id = bitstruct.unpack(
		'u16',
		network_id_bytes)[0]
	return network_id

# Function for parsing bytes from proxy positions characteristic
def parse_proxy_positions_bytes(proxy_positions_bytes):
	if len(proxy_positions_bytes) > 0:
		num_elements = proxy_positions_bytes[0]
		proxy_positions_bytes = proxy_positions_bytes[1:]
		proxy_positions_data = []
		for element_index in range(num_elements):
			position_bytes = proxy_positions_bytes[:15]
			proxy_positions_bytes = proxy_positions_bytes[15:]
			position_data = bitstruct.unpack_dict(
				'u16s32s32s32u8<',
				['node_id', 'x_position', 'y_position', 'z_position', 'quality'],
				position_bytes)
			proxy_positions_data.append(position_data)
		return proxy_positions_data
	else:
		return None

# Function for parsing bytes from device info characteristic
def parse_device_info_bytes(device_info_bytes):
	device_info_data = bitstruct.unpack_dict(
		'u64u32u32u32u32u32b1u7',
		[
			'node_id',
			'hw_version',
			'fw1_version',
			'fw2_version',
			'fw1_checksum',
			'fw2_checksum',
			'bridge',
			'unknown'],
		device_info_bytes)
	return device_info_data

# Function for parsing bytes from anchor list characteristic
def parse_anchor_list_bytes(anchor_list_bytes):
	if len(anchor_list_bytes) > 0:
		num_elements = anchor_list_bytes[0]
		anchor_list_bytes = anchor_list_bytes[1:]
		anchor_list_data = []
		for element_index in range(num_elements):
			node_id_bytes = anchor_list_bytes[:2]
			anchor_data_bytes = anchor_list_bytes[2:]
			node_id = bitstruct.unpack(
				'u16',
				node_id_bytes)
			anchor_list_data.append(node_id)
		return anchor_list_data
	else:
		return None

# Function for parsing bytes from operation mode characteristic
def parse_update_rate_bytes(update_rate_bytes):
	update_rate_data = bitstruct.unpack_dict(
		'u32u32',
		[
			'moving_update_rate',
			'stationary_update_rate'],
		update_rate_bytes)
	return update_rate_data

# Scan for BLE devices
print('\nScanning for BLE devices')
scanner = bluepy.btle.Scanner()
scan_entries = scanner.scan()
print('Finished scanning for BLE devices')

# Filter for Decawave devices
decawave_scan_entries = list(filter(is_decawave_scan_entry, scan_entries))
num_decawave_devices = len(decawave_scan_entries)
print('\nFound {} Decawave devices'.format(num_decawave_devices))

# Get data from Decawave devices
print('\nGetting data from Decawave devices')
decawave_devices = []
for decawave_scan_entry in decawave_scan_entries:
	mac_address = decawave_scan_entry.addr
	addrType = decawave_scan_entry.addrType
	iface = decawave_scan_entry.iface
	rssi = decawave_scan_entry.rssi
	connectable = decawave_scan_entry.connectable
	print('\nGetting data for Decawave device {}'.format(mac_address))
	# Get advertising data
	print('Getting advertising data')
	scan_data = decawave_scan_entry.getScanData()
	scan_data_information = []
	for scan_data_tuple in scan_data:
		type_code, description, value = scan_data_tuple
		if type_code == SHORT_LOCAL_NAME_TYPE_CODE:
			device_name = value
			print('Device name: {}'.format(device_name))
		scan_data_information.append({
			'type_code': type_code,
			'description': description,
			'value': value})
	# Connect to device
	print('Connecting to device')
	peripheral = bluepy.btle.Peripheral()
	peripheral.connect(mac_address)
	# Get services list
	print('Getting services list')
	services = list(peripheral.getServices())
	services_information = []
	for service in services:
		service_uuid = service.uuid
		# Get characteristics list
		print('Getting characteristics list for service {}'.format(service_uuid))
		characteristics = service.getCharacteristics()
		characteristics_information = []
		for characteristic in characteristics:
			characteristic_uuid = characteristic.uuid
			characteristics_information.append({
				'characteristic_uuid': characteristic_uuid})
		services_information.append({
			'service_uuid': service_uuid,
			'characteristics': characteristics_information})
	# Get network node service
	print('Getting network node service')
	network_node_service = peripheral.getServiceByUUID(NETWORK_NODE_SERVICE_UUID)
	# Get operation mode data
	print('Getting operation mode data')
	operation_mode_characteristic = network_node_service.getCharacteristics(OPERATION_MODE_CHARACTERISTIC_UUID)[0]
	operation_mode_bytes = operation_mode_characteristic.read()
	operation_mode_data = parse_operation_mode_bytes(operation_mode_bytes)
	# Get operation mode data
	print('Getting device info data')
	device_info_characteristic = network_node_service.getCharacteristics(DEVICE_INFO_CHARACTERISTIC_UUID)[0]
	device_info_bytes = device_info_characteristic.read()
	device_info_data = parse_device_info_bytes(device_info_bytes)
	# Get network ID
	print('Getting network ID')
	network_id_characteristic = network_node_service.getCharacteristics(NETWORK_ID_CHARACTERISTIC_UUID)[0]
	network_id_bytes = network_id_characteristic.read()
	network_id = parse_network_id_bytes(network_id_bytes)
	# Get location data mode data
	print('Getting location data mode data')
	location_data_mode_characteristic = network_node_service.getCharacteristics(LOCATION_DATA_MODE_CHARACTERISTIC_UUID)[0]
	location_data_mode_bytes = location_data_mode_characteristic.read()
	location_data_mode = parse_location_data_mode_bytes(location_data_mode_bytes)
	# Get location data
	print('Getting location data')
	location_data_characteristic = network_node_service.getCharacteristics(LOCATION_DATA_CHARACTERISTIC_UUID)[0]
	location_data_bytes = location_data_characteristic.read()
	location_data = parse_location_data_bytes(location_data_bytes)
	# Get proxy positions data
	print('Getting proxy positions data')
	proxy_positions_characteristic = network_node_service.getCharacteristics(PROXY_POSITION_CHARACTERISTIC_UUID)[0]
	proxy_positions_bytes = proxy_positions_characteristic.read()
	proxy_positions_data = parse_proxy_positions_bytes(proxy_positions_bytes)
	# Get anchor list data
	if DEVICE_TYPE_NAMES[operation_mode_data['device_type']] == 'Anchor'):
		print('Getting anchor list data')
		anchor_list_characteristic = network_node_service.getCharacteristics(ANCHOR_LIST_CHARACTERISTIC_UUID)[0]
		anchor_list_bytes = anchor_list_characteristic.read()
		anchor_list_data = parse_anchor_list_bytes(anchor_list_bytes)
	else:
		anchor_list_data = None
	# Get anchor list data
	if DEVICE_TYPE_NAMES[operation_mode_data['device_type']] == 'Tag'):
		print('Getting update rate data')
		update_rate_characteristic = network_node_service.getCharacteristics(TAG_UPDATE_RATE_CHARACTERISTIC_UUID)[0]
		update_rate_bytes = update_rate_characteristic.read()
		update_rate_data = parse_update_rate_bytes(update_rate_bytes)
	else:
		update_rate_data = None
	# Disconnect from device
	peripheral.disconnect()
	# Populate device data
	decawave_devices.append({
		'mac_address': mac_address,
		'device_name': device_name,
		'addrType': addrType,
		'iface': iface,
		'rssi': rssi,
		'connectable': connectable,
		'device_type': operation_mode_data['device_type'],
		'uwb_mode': operation_mode_data['uwb_mode'],
		'fw_version': operation_mode_data['fw_version'],
		'accelerometer_enable': operation_mode_data['accelerometer_enable'],
		'led_enable': operation_mode_data['led_enable'],
		'fw_update_enable': operation_mode_data['fw_update_enable'],
		'initiator': operation_mode_data['initiator'],
		'low_power_mode': operation_mode_data['low_power_mode'],
		'location_engine': operation_mode_data['location_engine'],
			'node_id',
			'hw_version',
			'fw1_version',
			'fw2_version',
			'fw1_checksum',
			'fw2_checksum',
			'bridge',
			'unknown'],
		'node_id': device_info_data['node_id'],
		'hw_version': device_info_data['hw_version'],
		'fw1_version': device_info_data['fw1_version'],
		'fw2_version': device_info_data['fw2_version'],
		'fw1_checksum': device_info_data['fw1_checksum'],
		'fw2_checksum': device_info_data['fw2_checksum'],
		'bridge': device_info_data['bridge'],
		'network_id': network_id,
		'location_data_mode': location_data_mode,
		'location_data': location_data,
		'proxy_positions_data': proxy_positions_data,
		'anchor_list_data': anchor_list_data,
		'update_rate_data': update_rate_data,
		'scan_data': scan_data_information,
		'services': services_information})

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
		file.write('RSSI: {} dB\n'.format(decawave_device['rssi']))
		file.write('Device type: {}\n'.format(DEVICE_TYPE_NAMES[decawave_device['device_type']]))
		file.write('Initiator: {}\n'.format(decawave_device['initiator']))
		file.write('UWB mode: {}\n'.format(UWB_MODE_NAMES[decawave_device['uwb_mode']]))
		file.write('Network ID: {}\n'.format(decawave_device['network_id']))
		file.write('Node ID: {:08X}\n'.format(decawave_device['node_id']))
		file.write('Hardware version: {}\n'.format(decawave_device['hw_version']))
		file.write('Firmware 1 version: {}\n'.format(decawave_device['fw1_version']))
		file.write('Firmware 2 version: {}\n'.format(decawave_device['fw2_version']))
		file.write('Firmware 1 checksum: {}\n'.format(decawave_device['fw1_checksum']))
		file.write('Firmware 2 checksum: {}\n'.format(decawave_device['fw2_checksum']))
		file.write('Bridge: {}\n'.format(decawave_device['bridge']))
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
			file.write('Moving update rate (ms): {}\n'.format(decawave_device['anchor_list_data']['moving_update_rate']))
			file.write('Stationary update rate (ms): {}\n'.format(decawave_device['anchor_list_data']['stationary_update_rate']))
