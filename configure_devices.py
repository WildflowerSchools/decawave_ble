import decawave_ble
from configuration_database import ConfigurationDatabaseCSVLocal as ConfigurationDatabase

# Function for configuring multiple devices from a database
def configure_devices_from_database(path):
	configuration_database = ConfigurationDatabase(path)
	print('Getting target device names')
	target_device_names = configuration_database.get_target_device_names()
	print('Target device names: {}'.format(target_device_names))
	devices = decawave_ble.scan_for_decawave_devices()
	device_names = list(devices.keys())
	target_devices_not_present = set(target_device_names) - set(device_names)
	if len(target_devices_not_present) > 0:
		raise ValueError('Target devices not present: {}'.format(target_devices_not_present))
	for target_device_name in target_device_names:
		print('Getting target data for {}'.format(target_device_name))
		target_data = configuration_database.get_target_data(target_device_name)
		print('Target data:\n{}'.format(target_data))
		print('Writing target data')
		decawave_ble.set_config(
			devices[target_device_name],
			device_type_name = target_data.get('device_type_name'),
			uwb_mode_name = target_data.get('uwb_mode_name'),
			accelerometer_enable = target_data.get('accelerometer_enable'),
			led_enable = target_data.get('led_enable'),
			initiator = target_data.get('initiator'),
			low_power_mode = target_data.get('low_power_mode'),
			location_engine = target_data.get('location_engine'),
			moving_update_rate = target_data.get('moving_update_rate'),
			stationary_update_rate = target_data.get('stationary_update_rate'),
			x_position = target_data.get('x_position'),
			y_position = target_data.get('y_position'),
			z_position = target_data.get('z_position'),
			quality = target_data.get('quality'))
