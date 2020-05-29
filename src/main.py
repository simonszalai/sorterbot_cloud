"""
Main module responsible for orchestrating image processing.

"""

import os
import cv2
import boto3
import traceback
import numpy as np
import concurrent.futures
from imutils import paths
import multiprocessing as mp
from yaml import load, Loader, YAMLError
from pathlib import Path
from dotenv import load_dotenv
import torchvision.transforms as transforms

from locator.detectron import Detectron
from vectorizer.vectorizer import Vectorizer
from utils.postgres import Postgres
from utils.logger import logger
from utils.S3 import S3
from utils.coord_conversion import object_to_polar, filter_duplicates


class Main:
    """
    Main class for controlling image processing. When instantiated, it loads all neccessary environment
    variables and config files and instantiates all needed modules.

    Parameters
    ----------
    base_img_path : str
        Location where the downloaded images should be stored.

    """

    def __init__(self, base_img_path):
        # Load environment from .env in project root
        load_dotenv()

        # Assign logger to main (this way tests can disable HTTPHandler)
        self.logger = logger

        # Parse config.yaml
        with open("config.yaml", 'r') as stream:
            try:
                config = load(stream, Loader)
            except YAMLError as error:
                self.logger.error("Error while opening config.yaml ", error)

        self.base_img_path = base_img_path

        if os.getenv("MODE") != "local":
            self.s3 = S3(base_img_path=self.base_img_path, logger_instance=self.logger)
            self.ssm = boto3.client("ssm")
            self.bucket_name = self.ssm.get_parameter(Name="SORTERBOT_BUCKET_NAME")["Parameter"]["Value"]

        self.postgres = Postgres()
        self.detectron = Detectron(
            base_img_path=self.base_img_path,
            model_config=config["DETECTRON"]["MODEL_CONFIG"],
            threshold=config["DETECTRON"]["THRESHOLD"]
        )
        self.vectorizer = Vectorizer(
            base_img_path=self.base_img_path,
            model_name=config["VECTORIZER"]["MODEL"],
            input_dimensions=config["VECTORIZER"]["INPUT_DIMS"],
            batch_size=config["VECTORIZER"]["BATCH_SIZE"]
        )

    def process_image(self, arm_id, session_id, image_name, img_bytes):
        """
        This method runs object recognition on the passed image and saves the result to the database.

        Parameters
        ----------
        session_id : str
            Datetime based unique identifier of the current session. It is generated by the Raspberry Pi and passed
            with the POST request.
        image_name : str
            Name of the image to be processed. The image has to be uploaded to the s3 bucket. Value is passed
            with the POST request.
        img_bytes : bytes
            Image to be processed as raw bytes.

        Returns
        -------
        success : bool
            Boolean indicating if processing was successful.

        """

        try:
            step = Path(image_name).stem
            log_args = {"arm_id": arm_id, "session_id": session_id, "log_type": step}
            self.logger.info(f"Image '{image_name} received, started processing.", dict(bm_id=2, **log_args))

            # Create table in Postgres for current session if it does not exist yet
            table_created = self.postgres.create_table(schema_name=arm_id, table_name=session_id)
            if table_created:
                self.logger.info(f"Postgres table created.", log_args)

            # Create folders for original and cropped images if they do not exist
            Path(os.path.join(self.base_img_path, session_id, "original")).mkdir(parents=True, exist_ok=True)
            Path(os.path.join(self.base_img_path, session_id, "cropped")).mkdir(parents=True, exist_ok=True)
            Path(os.path.join(self.base_img_path, session_id, "after")).mkdir(parents=True, exist_ok=True)
            Path(os.path.join(self.base_img_path, session_id, "bboxes_original")).mkdir(parents=True, exist_ok=True)
            Path(os.path.join(self.base_img_path, session_id, "bboxes_after")).mkdir(parents=True, exist_ok=True)

            # Convert image bytes to np.array and normalize it to ImageNet stats
            img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
            # normalize = transforms.Normalize(mean=[144., 142., 139.], std=[68., 69.7, 77.])
            # to_tensor = transforms.ToTensor()
            # img = normalize(to_tensor(img)).permute(1, 2, 0).numpy().astype("uint8")

            # Run detectron to get bounding boxes
            results = self.detectron.predict(session_id=session_id, image_name=image_name, img=img)
            self.logger.info(f"Bounding boxes predicted.", dict(bm_id=3, **log_args))

            # Insert bounding box locations to postgres
            self.postgres.insert_results(schema_name=arm_id, table_name=session_id, results=results)
            self.logger.info(f"Results saved to Postgres.", log_args)

            # Generate image paths on disk and s3
            img_disk_path = Path(self.base_img_path).joinpath(session_id, "original", image_name)
            img_s3_path = f'{arm_id}/{session_id}/{image_name}'

            # Write to disk and upload to s3 async
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            executor.submit(self.save_and_upload_image, img_disk_path, img_s3_path, img_bytes, log_args)

            self.logger.info(f"Processing image is successful.", dict(bm_id=7, **log_args))

            return True

        except Exception:
            traceback.print_exc()
            return False

    def save_and_upload_image(self, img_path, s3_path, img_bytes, log_args):
        """
        Takes an iamge as bytes and writes it to disk, then uploads it to s3. This functionality is not essential
        to generate the commands, so if this is executed on a separate thread, some speed-up can be gained.

        Parameters
        ----------
        img_path : str
            Path of the image where it should be saved to disk.
        s3_path : str
            Path of the image where it should be uploaded to s3.
        img_bytes : bytes
            The image as bytes.
        log_args : dict
            Arguments to correctly place log entry on the control panel.

        Returns
        -------
        success : bool
            Boolean representing if saving to disk and uploading to s3 was successful.

        """

        try:
            self.logger.info(f"Starting to save and upload image on a separate thread...", dict(bm_id=4, **log_args))

            # Write image bytes to disk for later use
            with open(img_path, "wb") as output_file:
                output_file.write(img_bytes)
            self.logger.info(f"Image written to disk.", dict(bm_id=5, **log_args))

            # Upload image to s3
            if os.getenv("MODE") != "local":
                self.s3.upload_file(self.bucket_name, img_path.as_posix(), s3_path)
                self.logger.info(f"Image uploaded to s3.", dict(bm_id=6, **log_args))

            return True
        except Exception as e:
            self.logger.error(e)
            return False

    def vectorize_session_images(self, arm_constants, session_id, should_stitch=True):
        """
        This method is to be executed after the last image of a session is processed. It gets a list of unique
        images in the current session, retrieves all the objects that belong to each image and runs the vectorizer
        on them.

        Parameters
        ----------
        arm_contants : dict
            Constants specific to the arm, defined in the arm's config file.
        session_id : str
            Unique identifier of the session.
        should_stitch : bool
            Boolean value that enables or disables stitching a panorama image.

        Returns
        -------
        pairings : list
            List of dicts containing pairs of objects and clusters.
        session_id : str
            Datetime based unique identifier of the current session. It is generated by the Raspberry Pi and passed
            with the POST request.
        stitching_process : process
            Process which is used for stitching. Should be joined after the commands are sent back to Raspberry Pi,
            this way the Pi is not waiting for it unneccessarily and also the process doesn't become zombie.

        """

        arm_id = arm_constants["arm_id"]
        log_args = {"arm_id": arm_id, "session_id": session_id, "log_type": "comm_gen"}

        self.logger.info("Generating session commands started.", dict(bm_id=9, **log_args))

        # Get list of unique image names in current session
        unique_images = self.postgres.get_unique_images(schema_name=arm_id, table_name=session_id)

        # Create separate lists of items and containers and convert them to absolute polar coordinates
        items = []
        conts = []
        images_with_objects = []
        unique_images = sorted(unique_images, key=lambda img: int(img.split(".")[0]))

        for image_name in unique_images:
            # Retrieve bounding boxes from postgres
            objects_of_image = self.postgres.get_objects_of_image(schema_name=arm_id, table_name=session_id, image_name=image_name)

            # Build list to stitch together images later
            images_with_objects.append({'image_name': image_name, "objects": objects_of_image})
            objects_of_image = sorted(objects_of_image, key=lambda obj: obj["id"])

            for obj in objects_of_image:
                # Transform coordinates to absolute polar coords
                (items if obj["class"] == 0 else conts).append(object_to_polar(arm_constants=arm_constants, image_name=image_name, obj=obj))

        # Stitch together session images
        stitching_process = None

        if should_stitch:
            try:
                self.stitch_images(arm_id, session_id, "original", images_with_objects)
            except Exception as e:
                print("stitch error", e)
            # stitching_process = mp.Process(target=self.stitch_images, args=(arm_id, session_id, "original", images_with_objects))
            # stitching_process.start()

        self.logger.info("Bounding boxes retrieved from database.", dict(bm_id=10, **log_args))

        # Filter out duplicates which are the same objects showing up on different images
        filtered_items = filter_duplicates(items)
        filtered_conts = filter_duplicates(conts)
        self.logger.info(f"Duplicate items filtered out.", log_args)

        # Handle case where there are more containers than objects
        if len(filtered_conts) > len(filtered_items):
            self.logger.warning(f"There are more containers than objects, skipping the excess.", log_args)
            filtered_conts = filtered_conts[: len(filtered_items)]

        # Handle case if no containers were found
        n_containers = len(filtered_conts)
        if n_containers == 0:
            self.logger.warning(f"No containers were found!", log_args)
            return [], [], stitching_process
        else:
            self.logger.info(f"{n_containers} containers were found.", log_args)

        self.logger.info(f"Absolute coordinates calculated and duplicates filtered.", dict(bm_id=15, **log_args))

        # Run vectorizer to assign each object to a cluster
        pairings = self.vectorizer.run(
            session_id=session_id,
            unique_images=unique_images,
            objects=filtered_items,
            n_containers=n_containers
        )
        self.logger.info(f"Vectorizer finished for all images.", log_args)

        # Return if no images were found
        if len(pairings) == 0:
            self.logger.warning(f"No objects were found!", log_args)
            return [], [], stitching_process

        def pairing_matches_item(pairing, item):
            return pairing["image_id"] == item["img_base_angle"] and pairing["obj_id"] == item["obj_id"]

        # Generate commands
        commands = []
        for item in filtered_items:
            target_cont = next(filtered_conts[pairing["cluster"]] for pairing in pairings if pairing_matches_item(pairing, item))
            commands.append((item["avg_polar_coords"], target_cont["avg_polar_coords"],))
        self.logger.info(f"Command generation finished.", dict(bm_id=16, **log_args))

        return commands, pairings, stitching_process

    def stitch_images(self, arm_id, session_id, stitch_type, images_with_objects):
        """
        Stitches together overlapping images to provide an overview on the UI about the area of interest before and after the
        arm's operation.

        Parameters
        ----------
        arm_id : str
            Unique identifier of the robot arm.
        session_id : str
            Datetime based unique identifier of the current session. It is generated by the Raspberry Pi and passed
            with the POST request.
        stitch_type : str
            Type of stitch which will be prepended to the file name. Possible values: original and after.
        images_with_objects : list of dicts
            List of dicts, each dictionary containing 'image_name' and 'objects'. There is one entry for each unique
            image in a session.

        """

        log_args = {"arm_id": arm_id, "session_id": session_id, "log_type": "comm_gen"}

        self.logger.info("Stitching images started.", dict(bm_id=11, **log_args))

        # Open images, draw bounding boxes then save them to a new directory
        for image in images_with_objects:
            # Open image for drawing and normalize it
            if stitch_type == "original":
                image_name = image["image_name"]
            else:
                image_name = image
            img_path = Path(self.base_img_path).joinpath(session_id, stitch_type, image_name)
            img = cv2.imread(img_path.as_posix())
            # cv2.normalize(img, img, 0, 255, cv2.NORM_MINMAX)

            # img = (img - img.mean(axis=(0, 1, 2), keepdims=True)) / img.std(axis=(0, 1, 2), keepdims=True)

            # normalize = transforms.Normalize(mean=[144., 142., 139.], std=[68., 69.7, 77.])
            # to_tensor = transforms.ToTensor()
            # img = normalize(to_tensor(img)).numpy()

            if stitch_type == "original":
                for obj in image["objects"]:
                    # Draw bounding boxes on image
                    cv2.rectangle(img, (obj["bbox_dims"]["x1"], obj["bbox_dims"]["y1"]), (obj["bbox_dims"]["x2"], obj["bbox_dims"]["y2"]), (255, 0, 0), 2)

            # Save image (with drawn bounding boxes in case of original stitch type)
            cv2.imwrite(Path(self.base_img_path).joinpath(session_id, f"bboxes_{stitch_type}", image_name).as_posix(), img)

        if stitch_type == "original":
            self.logger.info("Bounding boxes drawn and new images saved.", dict(bm_id=12, **log_args))
        else:
            self.logger.info("New images saved.", dict(bm_id=12, **log_args))

        image_paths_with_bb = sorted(list(paths.list_images(Path(self.base_img_path).joinpath(session_id, f"bboxes_{stitch_type}"))))
        basenames_with_bb = [Path(image_path).name for image_path in image_paths_with_bb]

        original_images = sorted(list(paths.list_images(Path(self.base_img_path).joinpath(session_id, "original"))))

        all_paths = []
        for orig_image in original_images:
            if Path(orig_image).name in basenames_with_bb:
                image_with_bb = next((path_with_bb for path_with_bb in image_paths_with_bb if Path(orig_image).name == Path(path_with_bb).name))
                all_paths.append(image_with_bb)
            else:
                all_paths.append(orig_image)

        # Open images for stitching
        images_with_bb = []
        for image_path_with_bb in all_paths:
            image_with_bb = cv2.imread(image_path_with_bb)
            images_with_bb.append(image_with_bb)

        # Stitch together images with bounding boxes
        stitcher = cv2.Stitcher_create(mode=1)

        (stitch_status, stitched_img) = stitcher.stitch(images_with_bb)

        if stitch_status == 0:
            # Save stitched image to disk
            self.logger.info("Image stitching successful.", dict(bm_id=13, **log_args))
            stitched_path = Path(self.base_img_path).joinpath(session_id, f"bboxes_{stitch_type}", f"{stitch_type}_stitch.jpg").as_posix()
            cv2.imwrite(stitched_path, stitched_img)
            log_args["log_type"] = "before" if stitch_type == "original" else "after"
            self.logger.info("Stitched image saved to disk.", dict(bm_id=14, **log_args))

            # Upload stitched image to s3
            if os.getenv("MODE") != "local":
                self.s3.upload_file(self.bucket_name, stitched_path, f'{arm_id}/{session_id}/{stitch_type}_stitch.jpg')
                self.logger.info("Stitched image uploaded to s3.", dict(bm_id=15, **log_args))

        else:
            self.logger.error("Image stitching failed!", log_args)
