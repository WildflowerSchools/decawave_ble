import bluepy.btle
import json
import collections
import bitstruct

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
PROXY_POSITIONS_CHARACTERISTIC_UUID = 'f4a67d7d-379d-4183-9c03-4b6ea5103291'
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

# Names of operation mode data values
DEVICE_TYPE_NAMES = ['Tag', 'Anchor']
UWB_MODE_NAMES = ['Off', 'Passive', 'Active']
FW_VERSION_NAMES = ['1', '2']

# Names of location data mode data values
LOCATION_DATA_MODE_NAMES = [
	'Position',
	'Distances',
	'Position and distances']

# Function for retrieving Decawave scan entries
def get_decawave_scan_entries():
	scanner = bluepy.btle.Scanner()
	scan_entries = scanner.scan()
	decawave_scan_entries = list(filter(is_decawave_scan_entry, scan_entries))
	return decawave_scan_entries

# Function for connecting to Decawave device
def get_decawave_peripheral(decawave_scan_entry):
	decawave_peripheral = bluepy.btle.Peripheral(decawave_scan_entry)
	return decawave_peripheral

# Function for connecting to Decawave network node service
def get_decawave_network_node_service(decawave_peripheral):
	decawave_network_node_service = decawave_peripheral.getServiceByUUID(NETWORK_NODE_SERVICE_UUID)
	return decawave_network_node_service

# Function for reading characteristic from Decawave network node service
# (identified by UUID)
def read_decawave_characteristic(decawave_peripheral, characteristic_uuid):
	decawave_network_node_service = get_decawave_network_node_service(decawave_peripheral)
	characteristic = decawave_network_node_service.getCharacteristics(characteristic_uuid)[0]
	bytes = characteristic.read()
	return(bytes)

# Function for writing characteristic to Decawave network node service
# (identified by UUID)
def write_decawave_characteristic(decawave_peripheral, characteristic_uuid, bytes):
	decawave_network_node_service = get_decawave_network_node_service(decawave_peripheral)
	characteristic = decawave_network_node_service.getCharacteristics(characteristic_uuid)[0]
	characteristic.write(bytes)

# Function for identifying Decawave devices from advertising data
def is_decawave_scan_entry(scan_entry):
	short_local_name = scan_entry.getValueText(SHORT_LOCAL_NAME_TYPE_CODE)
	return (short_local_name is not None and short_local_name.startswith('DW'))

# Function for getting scan data
def get_scan_data(decawave_scan_entry):
	advertising_data_tuples = decawave_scan_entry.getScanData()
	advertising_data = []
	for advertising_data_tuple in advertising_data_tuples:
		type_code, description, value = advertising_data_tuple
		advertising_data.append({
			'type_code': type_code,
			'description': description,
			'value': value})
	scan_data = {
		'mac_address': decawave_scan_entry.addr,
		'address_type': decawave_scan_entry.addrType,
		'interface': decawave_scan_entry.iface,
		'rssi': decawave_scan_entry.rssi,
		'connectable': decawave_scan_entry.connectable,
		'advertising_data': advertising_data}
	return scan_data

# Function for getting device name from scan data
def get_device_name(scan_data):
	device_name = None
	for advertising_datum in scan_data['advertising_data']:
		if advertising_datum['type_code'] == SHORT_LOCAL_NAME_TYPE_CODE:
			device_name = advertising_datum['value']
	return device_name

# Data and functions for parsing network node service characteristics
# (from documentation)

# Function for getting operation mode data
def get_operation_mode_data(decawave_peripheral):
	bytes = read_decawave_characteristic(
		decawave_peripheral,
		OPERATION_MODE_CHARACTERISTIC_UUID)
	data = parse_operation_mode_bytes(bytes)
	return(data)

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
	operation_mode_data['device_type_name'] = DEVICE_TYPE_NAMES[operation_mode_data['device_type']]
	operation_mode_data['uwb_mode_name'] = UWB_MODE_NAMES[operation_mode_data['uwb_mode']]
	operation_mode_data['fw_version_name'] = FW_VERSION_NAMES[operation_mode_data['fw_version']]
	return operation_mode_data

# Function for writing operation mode data
def write_operation_mode_data(decawave_peripheral, data):
	bytes = pack_operation_mode_bytes(data)
	write_decawave_characteristic(
		decawave_peripheral,
		OPERATION_MODE_CHARACTERISTIC_UUID,
		bytes)

# Function for packing bytes for persisted position characteristic
def pack_operation_mode_bytes(operation_mode_data):
	operation_mode_bytes = bitstruct.pack_dict(
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
		operation_mode_data)
	return operation_mode_bytes

# Function for getting location data mode data
def get_location_data_mode(decawave_peripheral):
	bytes = read_decawave_characteristic(
		decawave_peripheral,
		LOCATION_DATA_MODE_CHARACTERISTIC_UUID)
	data = parse_location_data_mode_bytes(bytes)
	return(data)

# Function for parsing bytes from location data mode characteristic
def parse_location_data_mode_bytes(location_data_mode_bytes):
	location_data_mode = location_data_mode_bytes[0]
	location_data_mode_name = LOCATION_DATA_MODE_NAMES[location_data_mode]
	location_data_mode_data = {
		'location_data_mode': location_data_mode,
		'location_data_mode_name': location_data_mode_name}
	return location_data_mode_data

# Function for getting location data
def get_location_data(decawave_peripheral):
	bytes = read_decawave_characteristic(
		decawave_peripheral,
		LOCATION_DATA_CHARACTERISTIC_UUID)
	data = parse_location_data_bytes(bytes)
	return(data)

# Function for parsing bytes from location data characteristic
def parse_location_data_bytes(location_data_bytes):
	if len(location_data_bytes) > 0:
		location_data_content = location_data_bytes[0]
		location_data_bytes = location_data_bytes[1:]
	else:
		location_data_content = None
	if (location_data_content == 0 or location_data_content == 2):
		position_bytes = location_data_bytes[:13]
		location_data_bytes = location_data_bytes[13:]
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

# Function for getting network ID
def get_network_id(decawave_peripheral):
	bytes = read_decawave_characteristic(
		decawave_peripheral,
		NETWORK_ID_CHARACTERISTIC_UUID)
	data = parse_network_id_bytes(bytes)
	return(data)

# Function for parsing bytes from network ID characteristic
def parse_network_id_bytes(network_id_bytes):
	if len(network_id_bytes) > 0:
		network_id = bitstruct.unpack(
			'u16<',
			network_id_bytes)[0]
		return network_id
	else:
		return None

# Function for getting proxy positions data
def get_proxy_positions_data(decawave_peripheral):
	bytes = read_decawave_characteristic(
		decawave_peripheral,
		PROXY_POSITIONS_CHARACTERISTIC_UUID)
	data = parse_proxy_positions_bytes(bytes)
	return(data)

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

# Function for getting device info data
def get_device_info_data(decawave_peripheral):
	bytes = read_decawave_characteristic(
		decawave_peripheral,
		DEVICE_INFO_CHARACTERISTIC_UUID)
	data = parse_device_info_bytes(bytes)
	return(data)

# Function for parsing bytes from device info characteristic
def parse_device_info_bytes(device_info_bytes):
	device_info_data = bitstruct.unpack_dict(
		'u64u32u32u32u32u32b1u7<',
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

# Function for getting anchor list data
def get_anchor_list_data(decawave_peripheral):
	bytes = read_decawave_characteristic(
		decawave_peripheral,
		ANCHOR_LIST_CHARACTERISTIC_UUID)
	data = parse_anchor_list_bytes(bytes)
	return(data)

# Function for parsing bytes from anchor list characteristic
def parse_anchor_list_bytes(anchor_list_bytes):
	if len(anchor_list_bytes) > 0:
		num_elements = anchor_list_bytes[0]
		anchor_list_bytes = anchor_list_bytes[1:]
		anchor_list_data = []
		for element_index in range(num_elements):
			node_id_bytes = anchor_list_bytes[:2]
			anchor_list_bytes = anchor_list_bytes[2:]
			node_id = bitstruct.unpack(
				'u16<',
				node_id_bytes)[0]
			anchor_list_data.append(node_id)
		return anchor_list_data
	else:
		return None

# Function for getting update rate data
def get_update_rate_data(decawave_peripheral):
	bytes = read_decawave_characteristic(
		decawave_peripheral,
		TAG_UPDATE_RATE_CHARACTERISTIC_UUID)
	data = parse_update_rate_bytes(bytes)
	return(data)

# Function for parsing bytes from update rate characteristic
def parse_update_rate_bytes(update_rate_bytes):
	update_rate_data = bitstruct.unpack_dict(
		'u32u32<',
		[
			'moving_update_rate',
			'stationary_update_rate'],
		update_rate_bytes)
	return update_rate_data

# Function for writing persisted position data
def write_persisted_position_data(decawave_peripheral, data):
	bytes = pack_persisted_position_bytes(data)
	write_decawave_characteristic(
		decawave_peripheral,
		ANCHOR_PERSISTED_POSITION_CHARACTERISTIC_UUID,
		bytes)

# Function for packing bytes for persisted position characteristic
def pack_persisted_position_bytes(persisted_position_data):
	persisted_position_bytes = bitstruct.pack_dict(
		's32s32s32u8<',
		['x_position', 'y_position', 'z_position', 'quality'],
		persisted_position_data)
	return persisted_position_bytes


