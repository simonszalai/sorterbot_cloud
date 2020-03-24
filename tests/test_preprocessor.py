import os
import shutil
import pytest
import hashlib
from mock_data import sample_preprocessor

from vectorizer.preprocessor import PreProcessor


class TestPreprocessor:
    @classmethod
    def setup_class(cls):
        # Construct test_images path and create temporary directory for testing
        cls.test_images_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "test_images"))
        cls.tmp_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "images/test_tmp"))
        os.makedirs(cls.tmp_path, exist_ok=True)

        # Copy files to temporary directory to be processed
        shutil.copytree(os.path.join(cls.test_images_path, "test-detectron"), os.path.join(cls.tmp_path, "original"))

        cls.preprocessor = PreProcessor(base_img_path=cls.tmp_path)

    @pytest.mark.parametrize('image_name, objects, checksums', sample_preprocessor)
    def test_crop_all_objects(self, image_name, objects, checksums):
        n_containers_of_image = self.preprocessor.crop_all_objects(image_name, objects)

        for i in range(2):
            cropped_img_path = os.path.join(self.tmp_path, "cropped", image_name, f"item_{i}.jpg")
            cropped_md5 = hashlib.md5(open(cropped_img_path, "rb").read()).hexdigest()

            assert checksums[i] == cropped_md5

        assert n_containers_of_image == 1

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.tmp_path)
