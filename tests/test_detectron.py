import os
import pytest
import shutil
from mock_data import exp_val_detectron

from locator.detectron import Detectron


class TestDetectron:
    @classmethod
    def setup_class(cls):
        # Construct test_images path and create temporary directory for testing
        cls.test_images_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "test_images"))
        cls.tmp_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "images/test_tmp"))
        os.makedirs(cls.tmp_path, exist_ok=True)

        # Copy files to temp directory be processed
        shutil.copytree(os.path.join(cls.test_images_path, "test-detectron"), os.path.join(cls.tmp_path, "original"))

        cls.detectron = Detectron(
            base_img_path=cls.tmp_path,
            model_config="COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
            threshold=0.5
        )

    @pytest.mark.parametrize('image_name, expected_results', exp_val_detectron)
    def test_predict(self, image_name, expected_results):
        results = self.detectron.predict(image_name)
        assert results == expected_results

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.tmp_path)
