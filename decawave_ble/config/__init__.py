
class ConfigurationDatabase:

    def get_target_device_names(self):
        """Returns a list of the device names associated with this configuration instance"""
        configuration_df = self.get_configuration()
        return list(configuration_df.keys())

    def get_configuration(self, force_reload=False):
        """Gets the configuration for this instance

        Keyword arguments:
        force_reload -- if true then the configuration data is reloaded rather than pulled from cache if it is cached (default False)
        """
        raise NotImplementedError()

    def get_target_data(
            self,
            target_device_name, force_reload=False):
        """Gets the target configuration

        Keyword arguments:
        target_device_name -- name of the target device as advertised by the decawave device
        force_reload -- if true then the configuration data is reloaded rather than pulled from cache if it is cached (default False)
        """
        configuration_dict = self.get_configuration(force_reload=False)
        return configuration_dict[target_device_name]
