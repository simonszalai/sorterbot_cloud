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
    This class sets up the s3 client (boto3) and provides methods to download and crop images.

    Parameters
    ----------
    base_img_path : str
        Absolute path where the downloaded images should be stored. Inside this folder, appropriate
        subfolders will be automatically created for the original images (named "original") and the
        cropped images (named "cropped").

    """

    def __init__(self, base_img_path):
        self.base_img_path = base_img_path

    def run(self, images):
        """
        This method coordinates the preprocessing. It loops though the provided list of images and
        crops all recognized objects from the image.

        Parameters
        ----------
        images : list
            List of dicts containing `image_name` and `objects` keys. The `objects` value is the return
            value of `postgres.get_objects_of_image()` function.

        Returns
        -------
        n_containers : int
            Number of objects classified as containers. Used as number of clusters by K-Means algorithm.

        """

        n_containers = 0
        for image in images:
            # Crop all items and count containers
            n_containers_of_image = self.crop_all_objects(image["image_name"], image["objects"])

            # Accumulate container count across images
            n_containers += n_containers_of_image

        return n_containers

    def crop_all_objects(self, image_name, objects):
        """
        This function crops all recognized items from an original image. It has been separated from
        `crop_object` for performance reasons (`Image.open()` is executed only once per image not once per object).

        Parameters
        ----------
        image_name : str
            Name of the image in the s3 bucket to be downloaded.
        objects : list
            List of dicts containing keys `id`, `type` and `bbox_dims`. `type` is the type of the recognized object
            (`item` or `container`), for details on `id` and `bbox_dims` see documentation of `crop_object` method.

        Returns
        -------
        n_containers : int
            Number of recognized containers on the current image

        """

        # Construct absolute path for current image
        img_path = os.path.join(self.base_img_path, "original", image_name)

        # Create folder with image name if it doesn't exist
        img_folder = os.path.join(self.base_img_path, "cropped", image_name)
        Path(img_folder).mkdir(parents=True, exist_ok=True)

        img = Image.open(img_path)

        logger.info(f"Cropping objects in {image_name}...")

        n_containers = 0
        for obj in objects:
            if obj["type"] == "container":
                # Increment container counter
                n_containers += 1
            else:  # elif obj["type"] == "item": TEMPORARY for testing
                # Crop only items, not containers
                self.crop_object(img_folder, img, obj["id"], obj["bbox_dims"])

        logger.info(f"Cropping objects in {image_name} finished!")

        img.close()

        return n_containers

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

        # Get image width and height in pixels
        total_w, total_h = img.size

        # Get bounding box corner coordinates in pixels
        left   = int(total_w * float(bbox_dims["x1"]))
        right  = int(total_w * float(bbox_dims["x2"]))
        top    = int(total_h * float(bbox_dims["y1"]))
        bottom = int(total_h * float(bbox_dims["y2"]))

        # Crop image around bounding box
        cropped_img = img.crop((left, top, right, bottom))

        # Save cropped image
        cropped_name = f"item_{id}.jpg"
        cropped_img.save(os.path.join(img_folder, cropped_name))
        logger.info(f"Cropped image '{cropped_name}' saved!")
