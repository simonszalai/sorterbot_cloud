import os
import boto3
from PIL import Image
from pathlib import Path


class PreProcessor:
    def __init__(self, base_path):
        self.s3 = boto3.resource("s3")
        self.base_path = base_path

    def download_image(self, image_name):
        img_path = os.path.join(self.base_path, "full", image_name)
        if not os.path.isfile(img_path):
            print(f"'{image_name}' does not exist on disk, downloading from S3...")
            self.s3.Bucket("sorterbot").download_file(image_name, img_path)
            print(f"'{image_name}' is successfully downloaded!")

    def crop_image(self, image_name, obj_id, bbox_dims):
        img_path = os.path.join(self.base_path, "full", image_name)

        # Open image
        img = Image.open(img_path)

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

        # Create folder with image name if it doesn't exist
        img_folder = os.path.join(self.base_path, "cropped", image_name)
        Path(img_folder).mkdir(parents=True, exist_ok=True)

        # Save cropped image
        cropped_name = f"obj_{obj_id}.jpg"
        cropped_img.save(os.path.join(img_folder, cropped_name))
        print(f"{image_name}/{cropped_name} saved!")
