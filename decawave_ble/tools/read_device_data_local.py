import decawave_ble
import logging
import argparse

def main():
    parser = argparse.ArgumentParser(
        description='Read data from devices and save to local text and JSON files.',
        epilog = 'Script will attempt to write a text file (e.g., my_output.txt) and a JSON file (e.g., my_output.json)'
    )
    parser.add_argument(
        'output_file_stem',
        help = 'output filename without extension (e.g., output/my_output)'
    )
    parser.add_argument(
        '-l',
        '--loglevel',
        help = 'log level (e.g., debug or warning or info)'
    )
    args = parser.parse_args()
    loglevel = args.loglevel
    if args.loglevel is not None:
        numeric_loglevel = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_loglevel, int):
            raise ValueError('Invalid log level: %s'.format(loglevel))
        logging.basicConfig(level=numeric_loglevel)
    # Paths for saving results
    output_file_stem = args.output_file_stem
    text_output_file = output_file_stem + '.txt'
    json_output_file = output_file_stem + '.json'
    # Scan for Decawave devices
    logging.info('Scanning for Decawave devices')
    decawave_devices = decawave_ble.scan_for_decawave_devices()
    num_decawave_devices = len(decawave_devices)
    logging.info('Found {} Decawave devices'.format(num_decawave_devices))
    # Get data from Decawave devices and write files
    logging.info('Getting data from Decawave devices')
    decawave_device_data = decawave_ble.get_data_multiple_devices(decawave_devices)
    decawave_ble.write_data_multiple_devices_to_json_local(
        decawave_device_data,
        json_output_file)
    decawave_ble.write_data_multiple_devices_to_text_local(
        decawave_device_data,
        text_output_file)

if __name__ == '__main__':
    main()
