import bluepy.btle
import bitstruct
import json

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
    'Position only',
    'Distances only',
    'Position and distances']

# Names of location data content values
LOCATION_DATA_CONTENT_NAMES = [
    'Position only',
    'Distances only',
    'Position and distances']

# Extend the default JSON encoder so it can handle bluepy.btle.UUID objects
class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
                if isinstance(obj, bluepy.btle.UUID):
                        return str(obj)
                return json.JSONencoder.default(self.obj)

# Class to represent a Decawave DWM1001 device
class DecawaveDevice:
    def __init__(
        self,
        decawave_scan_entry):
        self.scan_entry = decawave_scan_entry
        self.mac_address = decawave_scan_entry.addr
        self.address_type = decawave_scan_entry.addrType
        self.interface = decawave_scan_entry.iface
        self.rssi = decawave_scan_entry.rssi
        self.connectable = decawave_scan_entry.connectable
        advertising_data_tuples = decawave_scan_entry.getScanData()
        self.advertising_data = []
        self.device_name = None
        for advertising_data_tuple in advertising_data_tuples:
            type_code, description, value = advertising_data_tuple
            self.advertising_data.append({
                'type_code': type_code,
                'description': description,
                'value': value})
            if type_code == SHORT_LOCAL_NAME_TYPE_CODE:
                self.device_name = value

    def scan_data(self):
        return {
            'device_name': self.device_name,
            'mac_address': self.mac_address,
            'address_type': self.address_type,
            'interface': self.interface,
            'rssi': self.rssi,
            'connectable': self.connectable,
            'advertising_data': self.advertising_data}

# Function for finding Decawave devices:
def scan_for_decawave_devices():
    decawave_scan_entries = get_decawave_scan_entries()
    decawave_devices = {}
    for decawave_scan_entry in decawave_scan_entries:
        decawave_device = DecawaveDevice(decawave_scan_entry)
        decawave_devices[decawave_device.device_name] = decawave_device
    return decawave_devices

# Function for retrieving Decawave scan entries
def get_decawave_scan_entries():
    scanner = bluepy.btle.Scanner()
    scan_entries = scanner.scan()
    decawave_scan_entries = list(filter(is_decawave_scan_entry, scan_entries))
    return decawave_scan_entries

# Function for identifying Decawave devices from advertising data
def is_decawave_scan_entry(scan_entry):
    short_local_name = scan_entry.getValueText(SHORT_LOCAL_NAME_TYPE_CODE)
    return (short_local_name is not None and short_local_name.startswith('DW'))

# Function for connecting to Decawave device
def get_decawave_peripheral(decawave_device):
    decawave_peripheral = bluepy.btle.Peripheral(decawave_device.scan_entry)
    return decawave_peripheral

# Function for connecting to Decawave network node service
def get_decawave_network_node_service_from_peripheral(decawave_peripheral):
    decawave_network_node_service = decawave_peripheral.getServiceByUUID(NETWORK_NODE_SERVICE_UUID)
    return decawave_network_node_service

# Function for reading characteristic from Decawave network node service
# (identified by UUID)
def read_decawave_characteristic_from_peripheral(decawave_peripheral, characteristic_uuid):
    decawave_network_node_service = get_decawave_network_node_service_from_peripheral(decawave_peripheral)
    characteristic = decawave_network_node_service.getCharacteristics(characteristic_uuid)[0]
    bytes = characteristic.read()
    return bytes

# Function for writing characteristic to Decawave network node service
# (identified by UUID)
def write_decawave_characteristic_to_peripheral(decawave_peripheral, characteristic_uuid, bytes):
    decawave_network_node_service = get_decawave_network_node_service_from_peripheral(decawave_peripheral)
    characteristic = decawave_network_node_service.getCharacteristics(characteristic_uuid)[0]
    characteristic.write(bytes)

# Function for getting a complete set of data from device(s)
def get_data(decawave_device):
    device_name = decawave_device.device_name
    scan_data = decawave_device.scan_data()
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    operation_mode_data = get_operation_mode_data_from_peripheral(decawave_peripheral)
    device_info_data = get_device_info_data_from_peripheral(decawave_peripheral)
    network_id = get_network_id_from_peripheral(decawave_peripheral)
    location_data_mode_data = get_location_data_mode_data_from_peripheral(decawave_peripheral)
    location_data = get_location_data_from_peripheral(decawave_peripheral)
    proxy_positions_data = get_proxy_positions_data_from_peripheral(decawave_peripheral)
    anchor_list_data = get_anchor_list_data_from_peripheral(decawave_peripheral)
    update_rate_data = get_update_rate_data_from_peripheral(decawave_peripheral)
    decawave_peripheral.disconnect()
    data = {
        'device_name': device_name,
        'scan_data': scan_data,
        'operation_mode_data': operation_mode_data,
        'device_info_data': device_info_data,
        'network_id': network_id,
        'location_data_mode_data': location_data_mode_data,
        'location_data': location_data,
        'proxy_positions_data': proxy_positions_data,
        'anchor_list_data': anchor_list_data,
        'update_rate_data': update_rate_data}
    return data

def get_data_multiple_devices(decawave_devices):
    data_multiple = {}
    for device_name, decawave_device in decawave_devices.items():
        print('Getting data for {}'.format(device_name))
        data = get_data(decawave_device)
        data_multiple[device_name] = data
    return data_multiple

# Functions for setting all configuration parameters
def set_config(
    decawave_device,
    device_type_name = None,
    uwb_mode_name = None,
    accelerometer_enable = None,
    led_enable = None,
    initiator = None,
    low_power_mode = None,
    location_engine = None,
    moving_update_rate = None,
    stationary_update_rate = None,
    x_position = None,
    y_position = None,
    z_position = None,
    quality = None):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    set_operation_mode_to_peripheral(
        decawave_peripheral,
        device_type_name,
        uwb_mode_name,
        accelerometer_enable,
        led_enable,
        initiator,
        low_power_mode,
        location_engine)
    set_update_rate_to_peripheral(
        decawave_peripheral,
        moving_update_rate,
        stationary_update_rate)
    set_persisted_position_to_peripheral(
        decawave_peripheral,
        x_position,
        y_position,
        z_position,
        quality)
    decawave_peripheral.disconnect()

def write_data(
    decawave_device,
    data):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    write_operation_mode_data_to_peripheral(
        decawave_peripheral,
        data['operation_mode_data'])
    write_update_rate_data_to_peripheral(
        decawave_peripheral,
        data['update_rate_data'])
    write_persisted_position_data_to_peripheral(
        decawave_peripheral,
        data['persisted_position_data'])
    decawave_peripheral.disconnect()

# Functions for getting operation mode data
def get_operation_mode_data(decawave_device):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    data = get_operation_mode_data_from_peripheral(decawave_peripheral)
    decawave_peripheral.disconnect()
    return data

def get_operation_mode_data_from_peripheral(decawave_peripheral):
    bytes = read_decawave_characteristic_from_peripheral(
        decawave_peripheral,
        OPERATION_MODE_CHARACTERISTIC_UUID)
    data = parse_operation_mode_bytes(bytes)
    return data

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

# Functions for writing operation mode data

def set_operation_mode(
    decawave_device,
    device_type_name = None,
    uwb_mode_name = None,
    accelerometer_enable = None,
    led_enable = None,
    initiator = None,
    low_power_mode = None,
    location_engine = None):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    set_operation_mode_to_peripheral(
        decawave_peripheral,
        device_type_name,
        uwb_mode_name,
        accelerometer_enable,
        led_enable,
        initiator,
        low_power_mode,
        location_engine)
    decawave_peripheral.disconnect()

def set_operation_mode_to_peripheral(
    decawave_peripheral,
    device_type_name = None,
    uwb_mode_name = None,
    accelerometer_enable = None,
    led_enable = None,
    initiator = None,
    low_power_mode = None,
    location_engine = None):
    operation_mode_data = get_operation_mode_data_from_peripheral(decawave_peripheral)
    if device_type_name is not None:
        operation_mode_data['device_type_name'] = device_type_name,
        operation_mode_data['device_type'] = DEVICE_TYPE_NAMES.index(device_type_name)
    if uwb_mode_name is not None:
        operation_mode_data['uwb_mode_name'] = uwb_mode_name
        operation_mode_data['uwb_mode'] = UWB_MODE_NAMES.index(uwb_mode_name)
    if accelerometer_enable is not None:
        operation_mode_data['accelerometer_enable'] = accelerometer_enable
    if led_enable is not None:
        operation_mode_data['led_enable'] = led_enable
    if initiator is not None:
        operation_mode_data['initiator'] = initiator
    if low_power_mode is not None:
        operation_mode_data['low_power_mode'] = low_power_mode
    if location_engine is not None:
        operation_mode_data['location_engine'] = location_engine
    write_operation_mode_data_to_peripheral(
        decawave_peripheral,
        operation_mode_data)

def write_operation_mode_data(decawave_device, data):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    write_operation_mode_data_to_peripheral(decawave_peripheral, data)
    decawave_peripheral.disconnect()

def write_operation_mode_data_to_peripheral(decawave_peripheral, data):
    bytes = pack_operation_mode_bytes(data)
    write_decawave_characteristic_to_peripheral(
        decawave_peripheral,
        OPERATION_MODE_CHARACTERISTIC_UUID,
        bytes)

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

# Functions for getting location data mode data
def get_location_data_mode_data(decawave_device):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    data = get_location_data_mode_data_from_peripheral(decawave_peripheral)
    decawave_peripheral.disconnect()
    return data

def get_location_data_mode_data_from_peripheral(decawave_peripheral):
    bytes = read_decawave_characteristic_from_peripheral(
        decawave_peripheral,
        LOCATION_DATA_MODE_CHARACTERISTIC_UUID)
    data = parse_location_data_mode_bytes(bytes)
    return data

def parse_location_data_mode_bytes(location_data_mode_bytes):
    location_data_mode = location_data_mode_bytes[0]
    location_data_mode_name = LOCATION_DATA_MODE_NAMES[location_data_mode]
    location_data_mode_data = {
        'location_data_mode': location_data_mode,
        'location_data_mode_name': location_data_mode_name}
    return location_data_mode_data

# Functions for getting location data
def get_location_data(decawave_device):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    data = get_location_data_from_peripheral(decawave_peripheral)
    decawave_peripheral.disconnect()
    return data

def get_location_data_from_peripheral(decawave_peripheral):
    bytes = read_decawave_characteristic_from_peripheral(
        decawave_peripheral,
        LOCATION_DATA_CHARACTERISTIC_UUID)
    data = parse_location_data_bytes(bytes)
    return data

def parse_location_data_bytes(location_data_bytes):
    if len(location_data_bytes) > 0:
        location_data_content = location_data_bytes[0]
        location_data_bytes = location_data_bytes[1:]
        location_data_content_name = LOCATION_DATA_CONTENT_NAMES[location_data_content]
    else:
        location_data_content = None
        location_data_content_name = None
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
        'location_data_content': location_data_content,
        'location_data_content_name': location_data_content_name,
        'position_data': position_data,
        'distance_data': distance_data}

# Functions for getting network ID
def get_network_id(decawave_device):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    data = get_network_id_from_peripheral(decawave_peripheral)
    decawave_peripheral.disconnect()
    return data

def get_network_id_from_peripheral(decawave_peripheral):
    bytes = read_decawave_characteristic_from_peripheral(
        decawave_peripheral,
        NETWORK_ID_CHARACTERISTIC_UUID)
    data = parse_network_id_bytes(bytes)
    return data

def parse_network_id_bytes(network_id_bytes):
    if len(network_id_bytes) > 0:
        network_id = bitstruct.unpack(
            'u16<',
            network_id_bytes)[0]
        return network_id
    else:
        return None

# Functions for getting proxy positions data
def get_proxy_positions_data(decawave_device):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    data = get_proxy_positions_data_from_peripheral(decawave_peripheral)
    decawave_peripheral.disconnect()
    return data

def get_proxy_positions_data_from_peripheral(decawave_peripheral):
    bytes = read_decawave_characteristic_from_peripheral(
        decawave_peripheral,
        PROXY_POSITIONS_CHARACTERISTIC_UUID)
    data = parse_proxy_positions_bytes(bytes)
    return data

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

# Functions for getting device info data
def get_device_info_data(decawave_device):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    data = get_device_info_data_from_peripheral(decawave_peripheral)
    decawave_peripheral.disconnect()
    return data

def get_device_info_data_from_peripheral(decawave_peripheral):
    bytes = read_decawave_characteristic_from_peripheral(
        decawave_peripheral,
        DEVICE_INFO_CHARACTERISTIC_UUID)
    data = parse_device_info_bytes(bytes)
    return data

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

# Functions for getting anchor list data
def get_anchor_list_data(decawave_device):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    data = get_anchor_list_data_from_peripheral(decawave_peripheral)
    decawave_peripheral.disconnect()
    return data

def get_anchor_list_data_from_peripheral(decawave_peripheral):
    bytes = read_decawave_characteristic_from_peripheral(
        decawave_peripheral,
        ANCHOR_LIST_CHARACTERISTIC_UUID)
    data = parse_anchor_list_bytes(bytes)
    return data

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

# Functions for getting update rate data
def get_update_rate_data(decawave_device):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    data = get_update_rate_data_from_peripheral(decawave_peripheral)
    decawave_peripheral.disconnect()
    return data

def get_update_rate_data_from_peripheral(decawave_peripheral):
    bytes = read_decawave_characteristic_from_peripheral(
        decawave_peripheral,
        TAG_UPDATE_RATE_CHARACTERISTIC_UUID)
    data = parse_update_rate_bytes(bytes)
    return data

def parse_update_rate_bytes(update_rate_bytes):
    update_rate_data = bitstruct.unpack_dict(
        'u32u32<',
        [
            'moving_update_rate',
            'stationary_update_rate'],
        update_rate_bytes)
    return update_rate_data

# Functions for writing update rate data
def set_update_rate(
    decawave_device,
    moving_update_rate = None,
    stationary_update_rate = None):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    set_update_rate_to_peripheral(
        decawave_peripheral,
        moving_update_rate,
        stationary_update_rate)
    decawave_peripheral.disconnect()

def set_update_rate_to_peripheral(
    decawave_peripheral,
    moving_update_rate = None,
    stationary_update_rate = None):
    update_rate_data = get_update_rate_data_from_peripheral(decawave_peripheral)
    if moving_update_rate is not None:
        update_rate_data['moving_update_rate'] = moving_update_rate
    if stationary_update_rate is not None:
        update_rate_data['stationary_update_rate'] = stationary_update_rate
    write_update_rate_data_to_peripheral(
        decawave_peripheral,
        update_rate_data)

def write_update_rate_data(decawave_device, data):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    write_update_rate_data_to_peripheral(decawave_peripheral, data)
    decawave_peripheral.disconnect()

def write_update_rate_data_to_peripheral(decawave_peripheral, data):
    bytes = pack_update_rate_bytes(data)
    write_decawave_characteristic_to_peripheral(
        decawave_peripheral,
        TAG_UPDATE_RATE_CHARACTERISTIC_UUID,
        bytes)

def pack_update_rate_bytes(update_rate_data):
    update_rate_bytes = bitstruct.pack_dict(
        'u32u32<',
        [
            'moving_update_rate',
            'stationary_update_rate'],
        update_rate_data)
    return update_rate_bytes

# Functions for writing persisted position data
def set_persisted_position(
    decawave_device,
    x_position = None,
    y_position = None,
    z_position = None,
    quality = None):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    set_persisted_position_to_peripheral(
        decawave_peripheral,
        x_position,
        y_position,
        z_position,
        quality)
    decawave_peripheral.disconnect()

def set_persisted_position_to_peripheral(
    decawave_peripheral,
    x_position = None,
    y_position = None,
    z_position = None,
    quality = None):
    location_data = get_location_data_from_peripheral(decawave_peripheral)
    persisted_position_data = location_data['position_data']
    if persisted_position_data is None:
        persisted_position_data = {
            'x_position': 0,
            'y_position': 0,
            'z_position': 0,
            'quality': 100}
    if x_position is not None:
        persisted_position_data['x_position'] = x_position
    if y_position is not None:
        persisted_position_data['y_position'] = y_position
    if z_position is not None:
        persisted_position_data['z_position'] = z_position
    if quality is not None:
        persisted_position_data['quality'] = quality
    write_persisted_position_data_to_peripheral(
        decawave_peripheral,
        persisted_position_data)

def write_persisted_position_data(decawave_device, data):
    decawave_peripheral = get_decawave_peripheral(decawave_device)
    write_persisted_position_data_to_peripheral(decawave_peripheral, data)
    decawave_peripheral.disconnect()

def write_persisted_position_data_to_peripheral(decawave_peripheral, data):
    bytes = pack_persisted_position_bytes(data)
    write_decawave_characteristic_to_peripheral(
        decawave_peripheral,
        ANCHOR_PERSISTED_POSITION_CHARACTERISTIC_UUID,
        bytes)

def pack_persisted_position_bytes(persisted_position_data):
    persisted_position_bytes = bitstruct.pack_dict(
        's32s32s32u8<',
        ['x_position', 'y_position', 'z_position', 'quality'],
        persisted_position_data)
    return persisted_position_bytes

# Functions for outputting data from multiple Decawave devices
def write_data_multiple_devices_to_json_local(data_multiple, path):
    print('\nSaving results in {}'.format(path))
    with open(path, 'w') as file:
        json.dump(
            data_multiple,
            file,
            cls=CustomJSONEncoder,
            indent=2)

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

