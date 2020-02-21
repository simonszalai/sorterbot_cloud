import os
import pytest
import hashlib
from mock_data import sample_preprocessor

from utils.postgres import Postgres


class TestPostgres:
    @classmethod
    def setup_class(cls):
        cls.postgres = Postgres()

    def test_crop_all_objects(self, image_name, objects, checksums):
        n_containers_of_image = self.preprocessor.crop_all_objects(image_name, objects)

        for i in range(2):
            cropped_img_path = os.path.join(self.base_img_path, "cropped", image_name, f"item_{i}.jpg")
            cropped_md5 = hashlib.md5(open(cropped_img_path, "rb").read()).hexdigest()

            assert checksums[i] == cropped_md5

        assert n_containers_of_image == 1
