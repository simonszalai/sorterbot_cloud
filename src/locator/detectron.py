"""
This class uses Facebook Reserach's Detectron2 platform to localize and classify objects
on the provided image.

https://github.com/facebookresearch/detectron2

"""

import os
import cv2
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.logger import setup_logger

from utils.postgres import Postgres


class Detectron:
    """
    This class sets up Detectron2 and provides a method to predict objects on a provided image.

    Parameters
    ----------
    base_img_path : str
        Root directory for saved images. Inside the provided folder, the image to be
        processed should be saved inside the `original` directory.
    model_config : str
        Location of the Detectron config (.yaml) file inside the detectron2 repository's `config` folder.
        The value should contain any subfolders and the extension as well.
    threshold : float
        Object detection threshold for Detectron2.

    """

    def __init__(self, base_img_path, model_config, threshold=0.5):
        self.db = Postgres()

        self.base_img_path = base_img_path
        self.model_config = model_config
        self.threshold = threshold

        # Setup config
        self.cfg = get_cfg()
        self.cfg.merge_from_file(model_zoo.get_config_file(self.model_config))
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.threshold
        self.cfg.MODEL.DEVICE = "cpu"

        # Get pretrained weights
        self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(self.model_config)

        # Create predictor
        self.predictor = DefaultPredictor(self.cfg)

        setup_logger()

    def predict(self, image_name):
        """
        This method predicts the locations of bounding boxes on the provided image.

        Parameters
        ----------
        image_name : str
            Name of the image saved in the `images/original` folder.

        Returns
        -------
        boxes_as_relative : list
            List of dicts containing the results of the object detection as relative values as well
            as the original image name and the predicted class.

        """

        img = cv2.imread(os.path.join(self.base_img_path, "original", image_name))

        outputs = self.predictor(img)

        img_height = outputs["instances"].image_size[0]
        img_width = outputs["instances"].image_size[1]

        def abs_to_rel(box, cl):
            return {
                "image_name": image_name,
                "class": int(cl),
                "rel_x1": round(float(box[0]) / img_width, 4),
                "rel_y1": round(float(box[1]) / img_height, 4),
                "rel_x2": round(float(box[2]) / img_width, 4),
                "rel_y2": round(float(box[3]) / img_height, 4)
            }

        boxes = outputs["instances"].pred_boxes
        classes = outputs["instances"].pred_classes

        boxes_as_relative = [abs_to_rel(box, cl) for box, cl in zip(boxes, classes)]

        return boxes_as_relative
