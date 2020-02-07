
import os
import logging
from yaml import load, Loader, YAMLError
from pathlib import Path
from dotenv import load_dotenv

from locator.detectron import Detectron
from vectorizer.vectorizer import Vectorizer
from utils.postgres import Postgres
from utils.logger import logger


class Main:
    def __init__(self):
        # Load envirnoment vectorizer from .env in project root
        load_dotenv()
        logger.info('ASD')

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
        self.detectron = Detectron(base_img_path=self.base_img_path, config_file=config["DETECTRON_MODEL"])
        self.vectorizer = Vectorizer(
            base_img_path=self.base_img_path,
            model_name=config["VECTORIZER"]["MODEL"],
            input_dimensions=config["VECTORIZER"]["INPUT_DIMS"],
            batch_size=config["VECTORIZER"]["BATCH_SIZE"]
        )

    def process_image(self, session_id, img_name, is_final=0):
        # Open postgres connection and create table for current session if it does not exist yet
        self.postgres.open()
        self.postgres.create_table(table_name=session_id)

        # Run detectron to get bounding boxes
        results = self.detectron.predict(img_name=img_name)

        # Insert bounding box locations to postgres
        self.postgres.insert_results(results)

    def vectorize_session_images(self, session_id):
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
        pairings = self.vectorizer.run(bucket_name=session_id, images=images_with_objects)
        
        return pairings
