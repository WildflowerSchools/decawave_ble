from decawave_ble import configure_devices
from decawave_ble.config.csv import ConfigurationDatabaseCSVLocal
import logging
import argparse

def main():
    parser = argparse.ArgumentParser(
        description='Read configuration data from local file and write to devices.',
        epilog = 'A sample configuration data file is found in the package files in the config_data directory.'
    )
    parser.add_argument(
        'config_data_file',
        help = 'file containing config data in CSV format (e.g., my_config_data.csv)'
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
    logging.info('Configuring from database')
    configure_devices.configure_devices_from_database(ConfigurationDatabaseCSVLocal(args.config_data_file))

if __name__ == '__main__':
    main()
