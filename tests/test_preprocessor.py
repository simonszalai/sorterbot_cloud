import os
import shutil
import pytest
import hashlib
from pathlib import Path

from mock_data import sample_preprocessor
from vectorizer.preprocessor import PreProcessor


class TestPreprocessor:
    @classmethod
    def setup_class(cls):
        cls.session_id = "test_session_preproc"

        # Construct test_images path and create temporary directory for testing
        cls.test_images_path = Path(__file__).parent.joinpath("test_images", "test_preprocessor")
        cls.base_img_path = Path(__file__).parent.parent.joinpath("images")
        cls.tmp_path = cls.base_img_path.joinpath(cls.session_id)
        os.makedirs(cls.tmp_path.joinpath("cropped"), exist_ok=True)

        # Copy files to temporary directory to be processed
        shutil.copytree(cls.test_images_path, cls.tmp_path.joinpath("original"))

        cls.preprocessor = PreProcessor(base_img_path=cls.base_img_path)

    @pytest.mark.parametrize('image_name, objects, checksums', sample_preprocessor)
    def test_crop_all_objects(self, image_name, objects, checksums):
        self.preprocessor.crop_all_objects(self.session_id, image_name, objects)

        for i in range(2):
            cropped_img_path = os.path.join(self.tmp_path, "cropped", Path(image_name).stem, f"item_{i}.jpg")
            cropped_md5 = hashlib.md5(open(cropped_img_path, "rb").read()).hexdigest()

            assert checksums[i] == cropped_md5

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.tmp_path)
