import json
import os

import pandas as pd
import s3fs

from . import ConfigurationDatabase


class ConfigurationDatabaseCSVS3(ConfigurationDatabase):
    def __init__(
            self,
            configuration_database_bucket_name=None,
            configuration_database_object_name=None):
        if configuration_database_bucket_name is None:
            configuration_database_bucket_name = os.environ['CONFIGURATION_DATABASE_S3_BUCKET_NAME']
        if configuration_database_object_name is None:
            configuration_database_object_name = os.environ['CONFIGURATION_DATABASE_S3_OBJECT_NAME']
        self.configuration_database_bucket_name = configuration_database_bucket_name
        self.configuration_database_object_name = configuration_database_object_name

    def get_configuration(self):
        s3_location = 's3://' + self.configuration_database_bucket_name + '/' + self.configuration_database_object_name
        print('S3 location: {}'.format(s3_location))
        configuration_df = pd.read_csv(
            s3_location,
            index_col=0)
        return json.loads(configuration_df.to_json(orient='index'))

    def put_dataframe(
            self,
            configuration_df):
        s3 = s3fs.S3FileSystem(anon=False)
        s3_location = self.configuration_database_bucket_name + '/' + self.configuration_database_object_name
        bytes_to_write = configuration_df.to_csv(None).encode()
        with s3.open(s3_location, 'wb') as f:
            f.write(bytes_to_write)
