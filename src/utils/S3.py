"""
This class provides methods to interact with AWS s3 storage bucket.

"""

import os
import boto3
from PIL import Image
from pathlib import Path


class S3:
    """
    This class sets up the s3 client (boto3).

    Parameters
    ----------
    base_img_path : str
        Absolute path where the downloaded images should be stored. Inside this folder, appropriate
        subfolders will be automatically created for the original images (named "original") and the
        cropped images (named "cropped").
    logger_instance : logger
        Logger instance passed from main.

    """

    def __init__(self, base_img_path, logger_instance):
        session = boto3.Session(aws_access_key_id=os.getenv("AMAZON_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AMAZON_SECRET_ACCESS_KEY"))
        self.s3 = session.resource("s3")
        self.base_img_path = base_img_path
        self.logger = logger_instance

    def download_image(self, arm_id, session_id, image_name):
        """
        This method downloads images from s3. To avoid unneccessary downloads, images are only
        downloaded if they are missing or corrupted.

        Parameters
        ----------
        arm_id : str
            Unique identifier of the arm.
        session_id : str
            Datetime based unique identifier of the current session.
        image_name : str
            Name of the image in the s3 bucket to be downloaded.

        Returns
        -------
        img_path : str
            Absolute path of the downloaded image.

        """

        log_args = {"arm_id": arm_id, "session_id": session_id, "log_type": Path(image_name).stem}

        # Construct absolute path for current image
        img_path = os.path.join(self.base_img_path, session_id, "original", image_name)

        # Create folder if needed
        os.makedirs(os.path.dirname(img_path), exist_ok=True)

        if not os.path.isfile(img_path):
            self.s3.Bucket("sorterbot").download_file(f"{arm_id}/{session_id}/{image_name}", img_path)
            self.logger.info(f"Original image '{image_name}' is successfully downloaded!", log_args)
        else:
            try:
                im = Image.open(img_path)
                im.verify()
                im.close()
                self.logger.info(f"Original image '{image_name}' already exists on disk and it is valid, skipping download.", log_args)
            except Exception:
                self.logger.warning(f"Original image '{image_name}' already exists on disk, but it is corrupted, downloading again from s3...", log_args)
                self.s3.Bucket("sorterbot").download_file(f"{arm_id}/{session_id}/{image_name}", img_path)

        return img_path

    def upload_file(self, bucket_name, file_path, s3_path):
        """
        Uploads a file to s3.

        Parameters
        ----------
        bucket_name : str
            Name of the bucket to upload.
        file_path : str
            Path of the image to be uploaded.
        s3_path : str
            Path (including filename) where the file should be saved in s3.

        """

        self.s3.Bucket(bucket_name).upload_file(file_path, s3_path)
