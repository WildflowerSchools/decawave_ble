import pandas as pd
import boto3
import s3fs
import os

class ConfigurationDatabaseCSV:
	def get_target_device_names(self):
		configuration_df = self.get_dataframe()
		return configuration_df.index.tolist()

	def get_target_data(
		self,
		target_device_name):
		configuration_df = self.get_dataframe()
		return configuration_df.to_dict(orient='index')[target_device_name]

class ConfigurationDatabaseCSVS3(ConfigurationDatabaseCSV):
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

    def get_dataframe(self):
        s3_location = 's3://' + self.configuration_database_bucket_name +'/' + self.configuration_database_object_name
        print('S3 location: {}'.format(s3_location))
        configuration_df = pd.read_csv(
            s3_location,
            index_col=0)
        return configuration_df

    def put_dataframe(
        self,
        configuration_df):
        s3 = s3fs.S3FileSystem(anon=False)
        s3_location = self.configuration_database_bucket_name + '/' + self.configuration_database_object_name
        bytes_to_write = configuration_df.to_csv(None).encode()
        with s3.open(s3_location, 'wb') as f:
            f.write(bytes_to_write)

class ConfigurationDatabaseCSVLocal(ConfigurationDatabaseCSV):
    def __init__(
        self,
        configuration_database_local_path=None):
        if configuration_database_local_path is None:
            configuration_database_local_path = os.environ['CONFIGURATION_DATABASE_LOCAL_PATH']
        self.configuration_database_local_path = configuration_database_local_path

    def get_dataframe(self):
        configuration_df = pd.read_csv(
            self.configuration_database_local_path,
            index_col=0)
        return configuration_df

    def put_dataframe(
        self,
        configuration_df):
        configuration_df.to_csv(
            self.configuration_database_local_path)

