import os
import shutil
import pytest

from main import Main
from utils.postgres import Postgres
from mock_data import expected_main_results


class TestMain:
    @classmethod
    def setup_class(cls):
        # Create temporary directory for testing
        cls.tmp_path = os.path.join(os.path.abspath(os.path.join(os.path.abspath(__file__), "../../images")), "test_tmp")
        cls.db_name = "sorterbot_test"

        cls.main = Main(db_name=cls.db_name, base_img_path=cls.tmp_path)

    @pytest.mark.parametrize("image_name", ["valid_image.jpg", "corrupted_image.jpg", "missing_image.jpg"])
    def test_download_image(self, image_name):
        self.main.process_image("sorterbot_test_bucket", image_name)

    def test_vectorize_session_images(self):
        pairings = self.main.vectorize_session_images()
        print(pairings)

        shutil.rmtree(self.tmp_path)

        # Close connection to test database
        self.main.postgres.close()

        # Open another connection to maintenenace database so test database can be dropped
        self.main.postgres = Postgres(db_name="postgres")
        self.main.postgres.open()
        self.main.postgres.cursor.execute(f"DROP DATABASE IF EXISTS {self.db_name};")
        self.main.postgres.close()

        assert pairings == expected_main_results

    @classmethod
    def teardown_class(cls):
        # Drop table to prevent subsequent test failures
        cls.main.postgres.cursor.execute(f"DROP TABLE IF EXISTS {cls.table_name};")

        # Close connection to test database
        cls.main.postgres.close()

        # Open another connection to maintenenace database so test database can be dropped
        cls.main.postgres = Postgres(db_name="postgres")
        cls.main.postgres.open()
        cls.main.postgres.cursor.execute(f"DROP DATABASE IF EXISTS {cls.db_name};")
        cls.main.postgres.close()
