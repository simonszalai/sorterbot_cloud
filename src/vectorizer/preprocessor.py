"""
The PreProcessor module is responsible for fetching images from the AWS s3 bucket and cropping
the recognized objects from the original images.

"""


import os
from utils.logger import logger
from PIL import Image
from pathlib import Path


class PreProcessor:
    """
    This class provides methods to crop images.

    Parameters
    ----------
    base_img_path : str
        Absolute path where the downloaded images are stored. Inside this folder, appropriate
        subfolder will be automatically created for the cropped images (named "cropped").

    """

    def __init__(self, base_img_path):
        self.base_img_path = base_img_path

    def run(self, session_id, images):
        """
        This method coordinates the preprocessing. It loops though the provided list of images and
        crops all recognized objects from the image.

        Parameters
        ----------
        session_id : str
            Datetime based unique identifier of the current session. It is generated by the Raspberry Pi and passed
            with the POST request.
        images : list
            List of dicts containing `image_name` and `objects` keys. The `objects` value contains the bounding boxes
            to be cropped.

        """

        for image in images:
            # Crop all items
            self.crop_all_objects(session_id=session_id, image_name=image["image_name"], objects=image["objects"])

    def crop_all_objects(self, session_id, image_name, objects):
        """
        This function crops all recognized items from an original image. It has been separated from
        `crop_object` for performance reasons (`Image.open()` is executed only once per image not once per object).

        Parameters
        ----------
        session_id : str
            Datetime based unique identifier of the current session. It is generated by the Raspberry Pi and passed
            with the POST request.
        image_name : str
            Name of the image in the s3 bucket to be downloaded.
        objects : list
            List of dicts containing information about the recognized items. `bbox_dims` will be used here for cropping.

        """

        # Construct absolute path for current image
        img_path = os.path.join(self.base_img_path, session_id, "original", image_name)

        # Create folder with image name if it doesn't exist
        img_folder = os.path.join(self.base_img_path, session_id, "cropped", Path(image_name).stem)
        Path(img_folder).mkdir(parents=True, exist_ok=True)
        img = Image.open(img_path)

        logger.info(f"Cropping objects in {image_name}...")
        for obj in objects:
            self.crop_object(img_folder, img, obj["obj_id"], obj["bbox_dims"])
        logger.info(f"Cropping objects in {image_name} finished!")

        img.close()

    def crop_object(self, img_folder, img, id, bbox_dims):
        """
        This method should be called on each item (not containers) recognized on an image. It will
        crop the image around the provided bounding box coordinates and save the portion of the image
        inside the bounding box as a separate file. The cropped image will be placed in a folder
        corresponding to the name of the original image. The name of the new (cropped) image will
        contain `id`.

        Parameters
        ----------
        img_folder : str
            Absolute path of the folder where the current image's cropped pictures should be saved.
        img : Image
            Already opened image as PIL `Image` object, returned by `Image.open()`.
        id : int
            Object id (unique within an original image) of the recognized object.
            The cropped image will be saved with a name like the following: item_<id>.ext
        bbox_dims : dict
            Bounding box dimensions to be used for cropping. The dict should contain the following keys: `x1` and `y1`
            representing the coordinates of the top left, while `x2` and `y2` representing the coordinates of the
            bottom right corner of the bounding box. All values are floats between 0 and 1, representing relative distances.

        """

        # Crop image around bounding box
        cropped_img = img.crop((bbox_dims["x1"], bbox_dims["y1"], bbox_dims["x2"], bbox_dims["y2"]))

        # Save cropped image
        cropped_name = f"item_{id}.jpg"
        cropped_img.save(os.path.join(img_folder, cropped_name))
        logger.info(f"Cropped image '{cropped_name}' saved!")
