import os
import cv2
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.logger import setup_logger

from utils.postgres import Postgres


class Detectron:
    def __init__(self, base_path, config_file, threshold=0.5):
        self.db = Postgres()

        self.base_path = base_path
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

        setup_logger()

    def predict(self, img_name):
        img = cv2.imread(os.path.join(self.base_path, "original", img_name))

        outputs = self.predictor(img)

        img_height = outputs["instances"].image_size[0]
        img_width = outputs["instances"].image_size[1]

        def abs_to_rel(box, cl):
            abs_coords = {
                "abs_x1": float(box[0]),
                "abs_y1": float(box[1]),
                "abs_x2": float(box[2]),
                "abs_y2": float(box[3])
            }
            return (
                img_name,
                int(cl),
                round(abs_coords["abs_x1"] / img_width, 4),
                round(abs_coords["abs_y1"] / img_height, 4),
                round(abs_coords["abs_x2"] / img_width, 4),
                round(abs_coords["abs_y2"] / img_height, 4)
            )

        boxes = outputs["instances"].pred_boxes
        classes = outputs["instances"].pred_classes

        boxes_as_relative = [abs_to_rel(box, cl) for box, cl in zip(boxes, classes)]  # TODO use map instead?

        return boxes_as_relative
