
class ConfigurationDatabase:

    def get_target_device_names(self):
        """Returns a list of the device names associated with this configuration instance"""
        configuration_df = self.get_configuration()
        return list(configuration_df.keys())

    def get_configuration(self):
        """Gets the configuration for this instance

        Keyword arguments:
        """
        raise NotImplementedError()

    def get_target_data(
            self,
            target_device_name):
        """Gets the target configuration

        Keyword arguments:
        target_device_name -- name of the target device as advertised by the decawave device
        """
        configuration_dict = self.get_configuration()
        return configuration_dict[target_device_name]
