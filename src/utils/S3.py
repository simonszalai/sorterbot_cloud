"""
This class provides methods to interact with AWS s3 storage bucket.

"""

import os
from utils.logger import logger
import boto3
from PIL import Image


class S3:
    """
    This class sets up the s3 client (boto3).

    Parameters
    ----------
    base_img_path : str
        Absolute path where the downloaded images should be stored. Inside this folder, appropriate
        subfolders will be automatically created for the original images (named "original") and the
        cropped images (named "cropped").

    """

    def __init__(self, base_img_path):
        session = boto3.Session(aws_access_key_id=os.getenv("AMAZON_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AMAZON_SECRET_ACCESS_KEY"))
        self.s3 = session.resource("s3")
        self.base_img_path = base_img_path

    def download_image(self, session_id, image_name):
        """
        This method downloads images from s3. To avoid unneccessary downloads, images are only
        downloaded if they are missing or corrupted.

        Parameters
        ----------
        session_id : str
            Datetime based unique identifier of the current session.

        image_name : str
            Name of the image in the s3 bucket to be downloaded.

        Returns
        -------
        img_path : str
            Absolute path of the downloaded image.

        """

        # Construct absolute path for current image
        img_path = os.path.join(self.base_img_path, "original", image_name)

        if not os.path.isfile(img_path):
            logger.info(f"Original image '{image_name}' does not exist on disk, downloading from s3...")
            self.s3.Bucket("sorterbot").download_file(f"{session_id}/{image_name}", img_path)
            logger.info(f"Original image '{image_name}' is successfully downloaded!")
        else:
            try:
                im = Image.open(img_path)
                im.verify()
                im.close()
                logger.info(f"Original image '{image_name}' already exists on disk and it is valid, skipping download.")
            except Exception:
                logger.warning(f"Original image '{image_name}' already exists on disk, but it is corrupted, downloading again from s3...")
                self.s3.Bucket("sorterbot").download_file(f"{session_id}/{image_name}", img_path)

        return img_path
