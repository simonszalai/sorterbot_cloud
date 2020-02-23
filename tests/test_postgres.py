from mock_data import sample_data_for_postgres, exprected_unique_images, expected_objects_of_image_1

from utils.postgres import Postgres


class TestPostgres:
    @classmethod
    def setup_class(cls):
        cls.db_name = "sorterbot_test"
        cls.table_name = "test_table"
        cls.postgres = Postgres(db_name=cls.db_name)

    def test_open(self):
        self.postgres.open()

    def test_create_table(self):
        self.postgres.create_table(table_name=self.table_name)

    def test_insert_results(self):
        self.postgres.insert_results(sample_data_for_postgres)

    def test_get_unique_images(self):
        unique_images = self.postgres.get_unique_images()
        assert unique_images == exprected_unique_images

    def test_get_objects_of_image(self):
        objects_of_image = self.postgres.get_objects_of_image(image_name="sample_image_1.jpg")
        assert objects_of_image == expected_objects_of_image_1

    @classmethod
    def teardown_class(cls):
        # Drop table to prevent subsequent test failures
        cls.postgres.cursor.execute(f"DROP TABLE IF EXISTS {cls.table_name};")

        # Close connection to test database
        cls.postgres.close()

        # Open another connection to maintenenace database so test database can be dropped
        cls.postgres = Postgres(db_name="postgres")
        cls.postgres.open()
        cls.postgres.cursor.execute(f"DROP DATABASE IF EXISTS {cls.db_name};")
        cls.postgres.close()
