import os
from psycopg2 import pool
from mock_data import sample_data_for_postgres, expected_unique_images, expected_objects_of_image_1

from utils.postgres import Postgres


class TestPostgres:
    @classmethod
    def setup_class(cls):
        cls.schema_name = "test_schema"
        cls.table_name = "test_table"
        cls.postgres = Postgres()

    def test_create_table(self):
        self.postgres.create_table(schema_name=self.schema_name, table_name=self.table_name)

    def test_insert_results(self):
        self.postgres.insert_results(schema_name=self.schema_name, table_name=self.table_name, results=sample_data_for_postgres)

    def test_get_unique_images(self):
        unique_images = self.postgres.get_unique_images(schema_name=self.schema_name, table_name=self.table_name)
        print(unique_images)
        assert unique_images == expected_unique_images

    def test_get_objects_of_image(self):
        objects_of_image = self.postgres.get_objects_of_image(schema_name=self.schema_name, table_name=self.table_name, image_name="sample_image_1.jpg")
        print(objects_of_image)
        assert objects_of_image == expected_objects_of_image_1

    @classmethod
    def teardown_class(cls):
        # Drop schema to prevent subsequent test failures
        connection = cls.postgres.postgres_pool.getconn()
        cursor = connection.cursor()
        cursor.execute(f"DROP SCHEMA {cls.schema_name} CASCADE;")
        cls.postgres.postgres_pool.putconn(connection)
