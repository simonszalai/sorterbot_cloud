import os
import sys
import pytest
from mock_data import exp_val_detectron

sys.path.append(os.path.abspath('src'))
from locator.detectron import Detectron  # noqa: E402


class TestDetectron:
    @classmethod
    def setup_class(cls):
        cls.detectron = Detectron(
            base_img_path=os.path.abspath(os.path.join(os.path.abspath(__file__), "../test_images")),
            model_config="COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
            threshold=0.5
        )

    @pytest.mark.parametrize('image_name, expected_results', exp_val_detectron)
    def test_predict(self, image_name, expected_results):
        results = self.detectron.predict(image_name)
        assert results == expected_results
