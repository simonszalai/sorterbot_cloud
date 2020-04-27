import shutil
import hashlib
from imutils import paths
from pathlib import Path

from main import Main
from mock_data import expected_main_results, expected_stitched_md5


class TestMain:
    @classmethod
    def setup_class(cls):
        cls.arm_id = "TEST_ARM"
        cls.schema_name = "test_main_schema"
        cls.session_id = "test_main_session"
        cls.base_img_path = Path(__file__).parent.parent.joinpath("images")
        cls.test_images_path = Path(__file__).parent.joinpath("test_images", "test_main")
        cls.tmp_path = cls.base_img_path.joinpath(cls.session_id)

        # Copy test images to temporary session directory to be processed
        shutil.copytree(cls.test_images_path, cls.tmp_path.joinpath("original"))

        cls.main = Main(base_img_path=cls.base_img_path)

    def test_process_image(self):
        for img in list(paths.list_images(self.tmp_path.joinpath("original"))):
            self.main.process_image(arm_id=self.arm_id, session_id=self.session_id, image_name=Path(img).name)

    def test_vectorize_session_images(self):
        arm_constants = {
            "arm_id": self.arm_id,
            "arm_radius": 1500,
            "dist_max_as_pw": 2050,
            "dist_min_as_pw": 1150,
            "rotation_range_as_deg": 130,
            "rotation_range_as_pw": 1400
        }

        # Assert pairings
        commands, pairings = self.main.vectorize_session_images(arm_constants=arm_constants, session_id=self.session_id)

        def get_clusters(items):
            cluster_1 = []
            cluster_2 = []

            for item in items:
                if item["cluster"] == 0:
                    cluster_1.append(item["image_id"])
                elif item["cluster"] == 1:
                    cluster_2.append(item["image_id"])

            return cluster_1, cluster_2
        print(pairings)
        pairings_1, pairings_2 = get_clusters(pairings)
        expected_1, expected_2 = get_clusters(expected_main_results)

        # Order of clusters in the list is not consistent (as returned by K-Means algorithm) so both cases below should pass test
        # (The same elements are consistently in the same cluster, but sometimes cluster 0 is the previous run's cluster 1)
        assert (pairings_1 == expected_1 and pairings_2 == expected_2) or (pairings_2 == expected_1 and pairings_1 == expected_2)

        # Assert stitched image
        stitched_path = Path(self.base_img_path).joinpath(self.session_id, "bboxes", "before_stitch.jpg").as_posix()
        stitched_md5 = hashlib.md5(open(stitched_path, "rb").read()).hexdigest()
        assert stitched_md5 == expected_stitched_md5

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.tmp_path)

        # Clean up schema
        connection = cls.main.postgres.postgres_pool.getconn()
        cursor = connection.cursor()
        cursor.execute(f"DROP SCHEMA {cls.arm_id} CASCADE;")
        cls.main.postgres.postgres_pool.putconn(connection)
