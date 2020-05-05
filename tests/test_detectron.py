import os
import cv2
import shutil
import pytest
import numpy as np
from pathlib import Path
from mock_data import exp_val_detectron

from locator.detectron import Detectron


class TestDetectron:
    @classmethod
    def setup_class(cls):
        # Construct test_images path and create temporary directory for testing
        cls.test_images_path = Path(__file__).parent.joinpath("test_images", "test_detectron")
        cls.base_img_path = Path(__file__).parent.parent.joinpath("images")
        cls.tmp_path = cls.base_img_path.joinpath("test_session")

        # Remove files if they already exists and create directory
        shutil.rmtree(cls.tmp_path, ignore_errors=True)
        os.makedirs(cls.tmp_path, exist_ok=True)

        # Copy test images to temporary session directory to be processed
        shutil.copytree(cls.test_images_path, cls.tmp_path.joinpath("original"))

        cls.detectron = Detectron(
            base_img_path=cls.base_img_path.as_posix(),
            model_config="COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
            threshold=0.5
        )

    @pytest.mark.parametrize('image_name, expected_results', exp_val_detectron)
    def test_predict(self, image_name, expected_results):

        with open(self.tmp_path.joinpath("original", image_name), "rb") as image_file:
            img_bytes = image_file.read()
            img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
            results = self.detectron.predict("test_session", image_name, img)
            # print(results)
            assert results == expected_results

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.tmp_path)
