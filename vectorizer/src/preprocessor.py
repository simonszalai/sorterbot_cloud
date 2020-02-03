"""
The PreProcessor module is responsible for fetching images from the AWS s3 bucket and cropping
the recognized objects from the original images.

"""


import os
import boto3
from PIL import Image
from pathlib import Path


class PreProcessor:
    """
    This class sets up the s3 client (boto3) and provides methods to download and crop images.

    Parameters
    ----------
    base_path : str
        Absolute path where the downloaded images should be stored. Inside this folder, appropriate
        subfolders will be automatically created for the original images (named "original") and the
        cropped images (named "cropped").

    """

    def __init__(self, base_path, bucket_name):
        self.s3 = boto3.resource("s3")
        self.base_path = base_path
        self.bucket_name = bucket_name

        # Create folder for original images if it doesn't exist
        Path(os.path.join(self.base_path, "original")).mkdir(parents=True, exist_ok=True)

    def download_image(self, image_name):
        """
        This method downloads images from s3. To avoid unneccessary downloads, images are only
        downloaded if they are missing or corrupted.

        Parameters
        ----------
        image_name : str
            Name of the image in the s3 bucket to be downloaded.

        Returns
        -------
        img_path : str
            Absolute path of the downloaded image.

        """

        # Construct absolute path for current image
        img_path = os.path.join(self.base_path, "original", image_name)

        if not os.path.isfile(img_path):
            print(f"Original image '{image_name}' does not exist on disk, downloading from s3...")
            self.s3.Bucket(self.bucket_name).download_file(image_name, img_path)
            print(f"Original image '{image_name}' is successfully downloaded!")
        else:
            try:
                im = Image.open(img_path)
                im.verify()
                im.close()
                print(f"Original image '{image_name}' already exists on disk and it is valid, skipping download.")
            except:
                print(f"Original image '{image_name}' already exists on disk, but it is corrupted, downloading again from s3...")
                self.s3.Bucket(self.bucket_name).download_file(image_name, img_path)

        return img_path

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

        """
        # Construct absolute path for current image
        img_path = os.path.join(self.base_path, "original", image_name)

        # Create folder with image name if it doesn't exist
        img_folder = os.path.join(self.base_path, "cropped", image_name)
        Path(img_folder).mkdir(parents=True, exist_ok=True)

        img = Image.open(img_path)

        print(f"Cropping objects in {image_name}...")

        for obj in objects:
            # Crop only items, not containers
            if obj["type"] != "item":
                return
            self.crop_object(img_folder, img, obj["id"], obj["bbox_dims"])

        print(f"Cropping objects in {image_name} finished!")

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
            Bounding box dimensions to be used for cropping. The dict should contain the following keys: `w` (width),
            `h` (height), `x` (x coordinate of bounding box center) and `y` (y coordinate of bounding box center).
            All values are floats between 0 and 1, representing relative distances to the original image's appropriate
            dimensions.

        """

        # Get image width and height in pixels
        total_w, total_h = img.size

        # Get bounding box width and height in pixels
        bbox_w_px = int(total_w * bbox_dims["w"])
        bbox_h_px = int(total_h * bbox_dims["h"])

        # Get bounding box corner coordinates in pixels
        left   = int(total_w * bbox_dims["x"]) - bbox_w_px / 2
        right  = int(total_w * bbox_dims["x"]) + bbox_w_px / 2
        top    = int(total_h * bbox_dims["y"]) - bbox_h_px / 2
        bottom = int(total_h * bbox_dims["y"]) + bbox_h_px / 2

        # Crop image around bounding box
        cropped_img = img.crop((left, top, right, bottom))

        # Save cropped image
        cropped_name = f"item_{id}.jpg"
        cropped_img.save(os.path.join(img_folder, cropped_name))
        print(f"    Cropped image '{cropped_name}' saved!")
