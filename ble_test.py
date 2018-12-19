import bluepy.btle
import json
import collections
import bitstruct

class CustomJSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, bluepy.btle.UUID):
			return str(obj)
		return json.JSONencoder.default(self.obj)

# Path for saving results
output_path_stem = 'scan_results'
text_output_path = output_path_stem + '.txt'
json_output_path = output_path_stem + '.json'

# BLE advertising data type codes
SHORT_LOCAL_NAME_AD_CODE = 8

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

# Unknown Decawave characteristics for network node service (found in scan)
UNKNOWN_01_CHARACTERISTIC_UUID = 'f0f26c9b-2c8c-49ac-ab60-fe03def1b40c'
UNKNOWN_02_CHARACTERISTIC_UUID = '7bd47f30-5602-4389-b069-8305731308b6'
UNKNOWN_03_CHARACTERISTIC_UUID = '17b1613e-98f2-4436-bcde-23af17a10c72'
UNKNOWN_04_CHARACTERISTIC_UUID = '28d01d60-89de-4bfa-b6e9-651ba596232c'
UNKNOWN_05_CHARACTERISTIC_UUID = '5b10c428-af2f-486f-aee1-9dbd79b6bccb'

# Format strings (in bitstruct format) and field names for network
# node service characteristics (from documentation)

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

# Mappings from integer data values to names
DEVICE_TYPE_NAMES = ['Tag', 'Anchor']
UWB_MODE_NAMES = ['Off', 'Passive', 'Active']
FW_VERSION_NAMES = ['1', '2']

# Function for identifying Decawave devices
def is_decawave_scan_entry(scan_entry):
	short_local_name = scan_entry.getValueText(SHORT_LOCAL_NAME_AD_CODE)
	return (short_local_name is not None and short_local_name.startswith('DW'))

# Create scanner object
scanner = bluepy.btle.Scanner()

# Scan for BLE devices
print('Scanning for BLE devices.')
scan_entries = scanner.scan()
print('Finished scanning for BLE devices.')

# Filter for Decawave devices
decawave_scan_entries = list(filter(is_decawave_scan_entry, scan_entries))
num_decawave_devices = len(decawave_scan_entries)
print('Found {} Decawave devices.'.format(num_decawave_devices))

# Get services and characteristics for Decawave devices
print('Getting services and characteristics for Decawave devices.')
decawave_devices = []
for decawave_scan_entry in decawave_scan_entries:
	mac_address = decawave_scan_entry.addr
	addrType = decawave_scan_entry.addrType
	iface = decawave_scan_entry.iface
	rssi = decawave_scan_entry.rssi
	connectable = decawave_scan_entry.connectable
	print('\nGetting scan data for Decawave device {}'.format(mac_address))
	scan_data = decawave_scan_entry.getScanData()
	scan_data_information = []
	for scan_data_tuple in scan_data:
		type_code = scan_data_tuple[0]
		description = scan_data_tuple[1]
		value = scan_data_tuple[2]
		if type_code == 8:
			device_name = value
		scan_data_information.append({
			'type_code': type_code,
			'description': description,
			'value': value})
	peripheral = bluepy.btle.Peripheral()
	print('Connecting to Decawave device {}'.format(mac_address))
	peripheral.connect(mac_address)
	print('Getting services for Decawave device {}'.format(mac_address))
	services = list(peripheral.getServices())
	services_information = []
	for service in services:
		service_uuid = service.uuid
		print('Getting characteristics for service UUID: {}'.format(service_uuid))
		characteristics = service.getCharacteristics()
		characteristics_information = []
		for characteristic in characteristics:
			characteristic_uuid = characteristic.uuid
			characteristics_information.append({
				'characteristic_uuid': characteristic_uuid})
		services_information.append({
			'service_uuid': service_uuid,
			'characteristics': characteristics_information})
	print('Getting network node service')
	network_node_service = peripheral.getServiceByUUID(NETWORK_NODE_SERVICE_UUID)
	print('Getting operation mode data')
	operation_mode_characteristic = network_node_service.getCharacteristics(OPERATION_MODE_CHARACTERISTIC_UUID)[0]
	operation_mode_bytes = operation_mode_characteristic.read()
	operation_mode_data = OperationModeData(
		*bitstruct.unpack(
			OPERATION_MODE_FORMAT_STRING,
			operation_mode_bytes))
	peripheral.disconnect()
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
		file.write('\nDevice MAC address: {}\n'.format(decawave_device['mac_address']))
		file.write('\nDevice name: {}\n'.format(decawave_device['device_name']))
		file.write('Address type: {}\n'.format(decawave_device['addrType']))
		file.write('Interface number: {}\n'.format(decawave_device['iface']))
		file.write('RSSI (dB): {}\n'.format(decawave_device['rssi']))
		file.write('Connectable: {}\n'.format(decawave_device['connectable']))
		file.write('Device type: {}\n'.format(DEVICE_TYPE_NAMES[decawave_device['device_type']]))
		file.write('Initiator: {}\n'.format(decawave_device['initiator']))
		file.write('UWB mode: {}\n'.format(UWB_MODE_NAMES[decawave_device['uwb_mode']]))
		file.write('Firmware version: {}\n'.format(FW_VERSION_NAMES[decawave_device['fw_version']]))
		file.write('Firmware update enabled: {}\n'.format(decawave_device['fw_update_enable']))
		file.write('Accelerometer enabled: {}\n'.format(decawave_device['accelerometer_enable']))
		file.write('LED enabled: {}\n'.format(decawave_device['led_enable']))
		file.write('Low power mode: {}\n'.format(decawave_device['low_power_mode']))
		file.write('Location engine enabled: {}\n'.format(decawave_device['location_engine']))
		file.write('Advertising data:\n')
		for scan_data_item in decawave_device['scan_data']:
			file.write('  Type code: {}\n'.format(scan_data_item['type_code']))
			file.write('    Desc: {}\n'.format(scan_data_item['description']))
			file.write('    Value: {}\n'.format(scan_data_item['value']))
		file.write('Services:\n')
		for service in decawave_device['services']:
			file.write('  UUID: {}\n'.format(service['service_uuid']))
			file.write('  Characteristics:\n')
			for characteristic in service['characteristics']:
				file.write('    UUID: {}\n'.format(characteristic['characteristic_uuid']))

