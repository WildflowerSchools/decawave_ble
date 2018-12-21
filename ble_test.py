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

# Structure for BLE advertising data tuple
ADVERTISING_DATA_FIELD_NAMES = [
	'type_code',
	'description',
	'value']
AdvertisingData = collections.namedtuple(
	'AdvertisingData',
	ADVERTISING_DATA_FIELD_NAMES)

# BLE advertising data type codes
SHORT_LOCAL_NAME_TYPE_CODE = 8

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

# Format strings, field names, and data value names for network node service
# characteristics (from documentation)

# Operation mode characteristic
OPERATION_MODE_FORMAT_STRING = 'u1u2u1b1b1b1b1b1b1b1u4'
OPERATION_MODE_FIELD_NAMES = [
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
	'reserved_02']
OperationModeData = collections.namedtuple(
	'OperationModeData',
	OPERATION_MODE_FIELD_NAMES)

DEVICE_TYPE_NAMES = ['Tag', 'Anchor']
UWB_MODE_NAMES = ['Off', 'Passive', 'Active']
FW_VERSION_NAMES = ['1', '2']

# Location data mode characteristic
LOCATION_DATA_MODE_FORMAT_STRING = 'u8'
LOCATION_DATA_MODE_FIELD_NAMES = [
	'location_data_mode']
LocationDataModeData = collections.namedtuple(
	'LocationDataModeData',
	LOCATION_DATA_MODE_FIELD_NAMES)

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

# Function for identifying Decawave devices
def is_decawave_scan_entry(scan_entry):
	short_local_name = scan_entry.getValueText(SHORT_LOCAL_NAME_TYPE_CODE)
	return (short_local_name is not None and short_local_name.startswith('DW'))

# Scan for BLE devices
print('Scanning for BLE devices')
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
		advertising_data = AdvertisingData(*scan_data_tuple)
		if advertising_data.type_code == SHORT_LOCAL_NAME_TYPE_CODE:
			device_name = advertising_data.value
		scan_data_information.append({
			'type_code': advertising_data.type_code,
			'description': advertising_data.description,
			'value': advertising_data.value})
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
	operation_mode_data = OperationModeData(
		*bitstruct.unpack(
			OPERATION_MODE_FORMAT_STRING,
			operation_mode_bytes))
	# Get location data mode data
	print('Getting location data mode data')
	location_data_mode_characteristic = network_node_service.getCharacteristics(LOCATION_DATA_MODE_CHARACTERISTIC_UUID)[0]
	location_data_mode_bytes = location_data_mode_characteristic.read()
	location_data_mode_data = LocationDataModeData(
		*bitstruct.unpack(
			LOCATION_DATA_MODE_FORMAT_STRING,
			location_data_mode_bytes))
	# Get location data
	print('Getting location data')
	location_data_characteristic = network_node_service.getCharacteristics(LOCATION_DATA_CHARACTERISTIC_UUID)[0]
	location_data_bytes = location_data_characteristic.read()
	location_data_list = list(location_data_bytes)
	location_data = parse_location_data_bytes(location_data_bytes)
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
		'device_type': operation_mode_data.device_type,
		'uwb_mode': operation_mode_data.uwb_mode,
		'fw_version': operation_mode_data.fw_version,
		'accelerometer_enable': operation_mode_data.accelerometer_enable,
		'led_enable': operation_mode_data.led_enable,
		'fw_update_enable': operation_mode_data.fw_update_enable,
		'initiator': operation_mode_data.initiator,
		'low_power_mode': operation_mode_data.low_power_mode,
		'location_engine': operation_mode_data.location_engine,
		'location_data_mode': location_data_mode_data.location_data_mode,
		'location_data_list': location_data_list,
		'location_data': location_data,
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

