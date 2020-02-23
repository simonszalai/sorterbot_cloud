import os
import pytest

from utils.S3 import S3


class TestS3:
    @classmethod
    def setup_class(cls):
        cls.base_img_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../../images"))
        cls.s3 = S3(base_img_path=cls.base_img_path)

    @pytest.mark.parametrize('image_name', ["valid_image.jpg", "corrupted_image.jpg", "missing_image.jpg"])
    def test_download_image(self, image_name):
        self.s3.download_image("sorterbot_test_bucket", image_name)
