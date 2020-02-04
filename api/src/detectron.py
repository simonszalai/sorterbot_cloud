import cv2
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.logger import setup_logger


class Detectron:
    def __init__(self, config_file, threshold=0.5):
        setup_logger()
        self.config_file = config_file
        self.threshold = threshold

        # Setup config
        self.cfg = get_cfg()
        self.cfg.merge_from_file(model_zoo.get_config_file(self.config_file))
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.threshold

        # Get pretrained weights
        self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(self.config_file)

        # Create predictor
        self.predictor = DefaultPredictor(self.cfg)

    def predict(self, img_path):
        img = cv2.imread(img_path)
        outputs = self.predictor(img)

        return outputs
