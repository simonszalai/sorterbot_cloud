"""
Main module responsible for orchestrating image processing.

"""

import os
from yaml import load, Loader, YAMLError
from pathlib import Path
from dotenv import load_dotenv

from locator.detectron import Detectron
from vectorizer.vectorizer import Vectorizer
from utils.postgres import Postgres
from utils.logger import logger
from utils.S3 import S3


class Main:
    """
    Main class for controlling image processing. When instantiated, it loads all neccessary environment
    variables and config files and instantiates all needed modules.

    """
    def __init__(self):
        # Load envirnoment vectorizer from .env in project root
        load_dotenv()

        # Parse config.yaml
        with open("config.yaml", 'r') as stream:
            try:
                config = load(stream, Loader)
            except YAMLError as error:
                logger.error("Error while opening config.yaml ", error)

        # Construct base_img_path by moving 2 levels up from the current file's location
        self.base_img_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../images"))

        # Create folders for original and cropped images if they do not exist
        Path(os.path.join(self.base_img_path, "original")).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(self.base_img_path, "cropped")).mkdir(parents=True, exist_ok=True)

        self.postgres = Postgres()
        self.s3 = S3(base_img_path=self.base_img_path)
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

    def process_image(self, session_id, image_name):
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

        """

        # Open postgres connection and create table for current session if it does not exist yet
        self.postgres.open()
        self.postgres.create_table(table_name=session_id)

        # Download image if needed
        self.s3.download_image(session_id, image_name)

        # Run detectron to get bounding boxes
        results = self.detectron.predict(image_name=image_name)

        # TODO: duplicate checking

        # Insert bounding box locations to postgres
        self.postgres.insert_results(results)

    def vectorize_session_images(self):
        """
        This method is to be executed after the last image of a session is processed. It gets a list of unique
        images in the current session, retrieves all the objects that belong to each image and runs the vectorizer
        on them.

        Returns
        -------
        pairings : list
            List of dicts containing pairs of objects and clusters.

        """

        # Get list of unique image names in current session
        unique_images = self.postgres.get_unique_images()

        # Get objects belonging to each unique image from postgres
        images_with_objects = []
        for image_name in unique_images:
            images_with_objects.append({
                "image_name": image_name,
                "objects": self.postgres.get_objects_of_image(image_name=image_name)
            })

        # Terminate postgres connection as it's no longer needed
        self.postgres.close()

        # Run vectorizer to assign each object to a cluster
        pairings = self.vectorizer.run(images=images_with_objects)

        return pairings
