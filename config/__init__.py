
class ConfigurationDatabase:

    def get_target_device_names(self):
        # TODO - validate how this should be working
        configuration_df = self.get_configuration()
        return list(configuration_df.keys())

    def get_configuration(self, force_reload=False):
        raise NotImplementedError()

    def get_target_data(
            self,
            target_device_name, force_reload=False):
        configuration_dict = self.get_configuration(force_reload=False)
        return configuration_dict[target_device_name]
