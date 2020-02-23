import os
import pytest
import shutil
from PIL import Image

from utils.S3 import S3


class TestS3:
    @classmethod
    def setup_class(cls):
        cls.base_img_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../images"))

        # Create temporary directory for testing
        cls.tmp_path = os.path.join(cls.base_img_path, "test_tmp")

        # Copy 2 images (valid and corrupted) to temp dir for testing
        shutil.copytree(os.path.join(cls.base_img_path, "test"), os.path.join(cls.tmp_path, "original"))

        # Init S3 with temp path
        cls.s3 = S3(base_img_path=cls.tmp_path)

    @pytest.mark.parametrize('image_name', ["valid_image.jpg", "corrupted_image.jpg", "missing_image.jpg"])
    def test_download_image(self, image_name):
        self.s3.download_image("sorterbot_test_bucket", image_name)

        # Verify downloaded image
        im = Image.open(os.path.join(os.path.join(self.tmp_path, "original"), image_name))
        im.verify()
        im.close()

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.tmp_path)
