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
        cls.table_name = "test_table"

        cls.main = Main(db_name=cls.db_name, base_img_path=cls.tmp_path)

    @pytest.mark.parametrize("image_name", ["valid_image.jpg", "corrupted_image.jpg", "missing_image.jpg"])
    def test_process_image(self, image_name):
        self.main.process_image(session_id="sorterbot_test_bucket", image_name=image_name)

    def test_vectorize_session_images(self):
        pairings = self.main.vectorize_session_images()

        shutil.rmtree(self.tmp_path)

        def get_clusters(items):
            cluster_1 = []
            cluster_2 = []

            for item in items:
                if item["cluster"] == 0:
                    cluster_1.append(item["filename"])
                elif item["cluster"] == 1:
                    cluster_2.append(item["filename"])

            return cluster_1, cluster_2

        pairings_1, pairings_2 = get_clusters(pairings)
        expected_1, expected_2 = get_clusters(expected_main_results)

        # Order of clusters in the list is not consistent (as returned by K-Means algorithm) so both cases below should pass test
        # (The same elements are consistently in the same cluster, but sometimes cluster 0 is the previous run's cluster 1)
        assert (pairings_1 == expected_1 and pairings_2 == expected_2) or (pairings_2 == expected_1 and pairings_1 == expected_2)

    @classmethod
    def teardown_class(cls):
        # Close connection to test database
        cls.main.postgres.close()
        print("closed")
        # Open another connection to maintenance database so test database can be dropped
        cls.main.postgres = Postgres(db_name="postgres")
        print("created")
        cls.main.postgres.open()
        print("opened")
        cls.main.postgres.cursor.execute(f"DROP DATABASE IF EXISTS {cls.db_name};")
        print("executed")
        cls.main.postgres.close()
        print("closed again")
