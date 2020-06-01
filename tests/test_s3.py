import os
import boto3
import pytest
import shutil
from PIL import Image
from pathlib import Path

from utils.S3 import S3
from utils.logger import logger


class TestS3:
    @classmethod
    def setup_class(cls):
        session = boto3.Session(region_name=os.getenv("DEPLOY_REGION"))
        cls.ssm = session.client('ssm')
        cls.bucket_name = f'sorterbot-{cls.ssm.get_parameter(Name="RESOURCE_SUFFIX")["Parameter"]["Value"]}'
        cls.arm_id = "TEST_ARM"
        cls.session_id = "test_session_s3"

        # Construct test_images path and create temporary directory for testing
        cls.test_images_path = Path(__file__).parent.joinpath("test_images", "test_s3")
        cls.base_img_path = Path(__file__).parent.parent.joinpath("images")
        cls.tmp_path = cls.base_img_path.joinpath(cls.session_id)
        os.makedirs(cls.tmp_path.joinpath("original"), exist_ok=True)

        # Disable HTTPHandler for logging
        logger.handlers = []

        # Init S3 with base path
        cls.s3 = S3(base_img_path=cls.base_img_path.as_posix(), logger_instance=logger)

        # Copy 2 images (valid and corrupted) to temp dir for testing
        shutil.copy(cls.test_images_path.joinpath("corrupted_image.jpg"), Path(cls.tmp_path).joinpath("original", "corrupted_image.jpg"))
        shutil.copy(cls.test_images_path.joinpath("valid_image.jpg"), Path(cls.tmp_path).joinpath("original", "valid_image.jpg"))

        # Upload third image to bucket
        cls.s3.upload_file(
            cls.bucket_name,
            cls.test_images_path.joinpath("missing_image.jpg").as_posix(),
            f"{cls.arm_id}/{cls.session_id}/{'missing_image.jpg'}"
        )

    @pytest.mark.parametrize("image_name", ["valid_image.jpg", "corrupted_image.jpg"])
    def test_upload_image(self, image_name):
        self.s3.upload_file(
            self.bucket_name,
            Path(self.tmp_path).joinpath("original", image_name).as_posix(),
            f"{self.arm_id}/{self.session_id}/{image_name}"
        )

    @pytest.mark.parametrize("image_name", ["valid_image.jpg", "corrupted_image.jpg", "missing_image.jpg"])
    def test_download_image(self, image_name):
        self.s3.download_image(self.arm_id, self.session_id, image_name)

        def verify_image():
            im = Image.open(Path(self.tmp_path).joinpath("original", image_name))
            im.verify()
            im.close()

        # Verify downloaded image
        if image_name == "corrupted_image.jpg":
            with pytest.raises(IOError):
                verify_image()
        else:
            verify_image()

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.tmp_path)
        for image_name in ["valid_image.jpg", "corrupted_image.jpg", "missing_image.jpg"]:
            cls.s3.s3.Object(cls.bucket_name, f"{cls.arm_id}/{cls.session_id}/{image_name}").delete()
