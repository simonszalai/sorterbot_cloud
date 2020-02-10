import os
import pytest
from locator.detectron import Detectron
from expected_values import exp_val_detectron


class TestDetectron:
    @pytest.fixture(autouse=True, scope='function')  # QUESTION: with scope='class', I get the error:  AttributeError: 'TestDetectron' object has no attribute 'detectron'. Why?  # noqa: E501
    def init(self):
        self.detectron = Detectron(
            base_img_path=os.path.abspath(os.path.join(os.path.abspath(__file__), "../test_images")),
            model_config="COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
            threshold=0.5
        )

    @pytest.mark.parametrize('image_name, expected_results', exp_val_detectron)
    def test_predict(self, image_name, expected_results):
        results = self.detectron.predict(image_name)
        assert results == expected_results
