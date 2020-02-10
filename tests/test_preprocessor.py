import os
import pytest
import hashlib

from vectorizer.preprocessor import PreProcessor
from mock_data import sample_preprocessor


class TestPreprocessor:
    @pytest.fixture(autouse=True, scope='function')
    def init(self):
        self.base_img_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "../test_images"))
        self.preprocessor = PreProcessor(base_img_path=self.base_img_path)

    @pytest.mark.parametrize('image_name, objects, checksums', sample_preprocessor)
    def test_crop_all_objects(self, image_name, objects, checksums):
        n_containers_of_image = self.preprocessor.crop_all_objects(image_name, objects)

        for i in range(2):
            cropped_img_path = os.path.join(self.base_img_path, "cropped", image_name, f"item_{i}.jpg")
            cropped_md5 = hashlib.md5(open(cropped_img_path, "rb").read()).hexdigest()

            assert checksums[i] == cropped_md5

        assert n_containers_of_image == 1
