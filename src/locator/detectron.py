"""
This class uses Facebook Reserach's Detectron2 platform to localize and classify objects
on the provided image.

https://github.com/facebookresearch/detectron2

"""

import os
import cv2
import numpy as np
from pathlib import Path
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.logger import setup_logger


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

    def __init__(self, base_img_path, model_config, threshold=0.7):
        self.base_img_path = base_img_path
        self.model_config = model_config
        self.threshold = threshold

        # Setup config
        self.cfg = get_cfg()
        self.cfg.merge_from_file(model_zoo.get_config_file(self.model_config))
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.threshold
        self.cfg.MODEL.DEVICE = "cpu"
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = 2

        # Get pretrained weights
        self.cfg.MODEL.WEIGHTS = Path(__file__).parents[2].joinpath("weights", "model_final.pth").resolve().as_posix()

        # Create predictor
        self.predictor = DefaultPredictor(self.cfg)

        setup_logger()

    def predict(self, session_id, image_name, img):
        """
        This method predicts the locations of bounding boxes on the provided image.

        Parameters
        ----------
        session_id : str
            Datetime based unique identifier of the current session. It is generated by the Raspberry Pi and passed
            with the POST request.
        image_name : str
            Name of the image saved in the `images/original` folder.
        img : np.array
            Image to be processed as Numpy array.

        Returns
        -------
        results : list
            List of dicts containing the results of the object detection as absolute pixel values as well
            as the original image name, dimensions and the predicted class.

        """

        # Use Detectron2 to predict bounding boxes
        outputs = self.predictor(img)

        img_height = outputs["instances"].image_size[0]
        img_width = outputs["instances"].image_size[1]

        def create_result(box, cl):
            return {
                "image_name": image_name,
                "image_width": img_width,
                "image_height": img_height,
                "class": int(cl),
                "x1": int(box[0]),
                "y1": int(box[1]),
                "x2": int(box[2]),
                "y2": int(box[3])
            }

        boxes = outputs["instances"].pred_boxes
        classes = outputs["instances"].pred_classes

        results = [create_result(box, cl) for box, cl in zip(boxes, classes)]

        return results
