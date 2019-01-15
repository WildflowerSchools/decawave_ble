from . import ConfigurationDatabase


class HoneycombConfigurationDatabase(ConfigurationDatabase):

    def __init__(self, honeycomb_client, environment_id):
        """Wrapper to use honeycomb api for configuration data

        Keyword arguments:
        honeycomb_client -- an instance of a `honeycomb.HoneycombClient`
        environment_id -- the id of the honeycomb environment to load devices for
        """
        self.honeycomb_client = honeycomb_client
        self.environment_id = environment_id

    def get_configuration(self, force_reload=False):
        return dict()
