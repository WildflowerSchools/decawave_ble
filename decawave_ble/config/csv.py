import json
import os

import pandas as pd

from . import ConfigurationDatabase


class ConfigurationDatabaseCSVLocal(ConfigurationDatabase):
    def __init__(
            self,
            configuration_database_local_path=None):
        if configuration_database_local_path is None:
            configuration_database_local_path = os.environ['CONFIGURATION_DATABASE_LOCAL_PATH']
        self.configuration_database_local_path = configuration_database_local_path

    def get_configuration(self):
        configuration_df = pd.read_csv(
            self.configuration_database_local_path,
            index_col=0)
        return json.loads(configuration_df.to_json(orient='index'))

    def put_dataframe(
            self,
            configuration_df):
        configuration_df.to_csv(
            self.configuration_database_local_path)
