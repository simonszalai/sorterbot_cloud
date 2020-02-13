"""
Utility class to provide methods to interact with the PostgreSQL database deployed to Amazon's RDS service.

"""

import os
import psycopg2
from utils.logger import logger
from psycopg2.extras import execute_values


class Postgres:
    def open(self):
        """
        This method opens a connection to the database using connection credentials provided as
        environment variables.

        """

        try:
            self.connection = psycopg2.connect(
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_NAME")
            )
            self.connection.autocommit = True

            self.cursor = self.connection.cursor()

        except psycopg2.Error as error:
            raise Exception(f"Error while connecting to PostgreSQL: {error.pgerror}") from error

    def create_table(self, table_name="sorterbot"):
        """
        This method creates a new table with a given name in the database if it does not exist yet. A separate
        table should be created for each session.

        Parameters
        ----------
        table_name : str
            Name of the table to be created. Should be the `session_id`.

        """

        try:
            # Since postgres converts table names to lowercase, this is needed to avoid unexpected behavior
            self.table_name = table_name.lower()

            check_table_query = f"SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='{table_name}');"
            self.cursor.execute(check_table_query)
            table_exists = self.cursor.fetchone()[0]

            if table_exists:
                logger.info(f"Table '{table_name}' already exists, skipping table creation...")
                return

            create_table_query = f"""
                CREATE TABLE {table_name} (
                    id SERIAL PRIMARY KEY,
                    image_name TEXT,
                    class TEXT,
                    rel_x1 TEXT,
                    rel_y1 TEXT,
                    rel_x2 TEXT,
                    rel_y2 TEXT
                );
            """

            self.cursor.execute(create_table_query)

        except psycopg2.Error as error:
            logger.exception(error)
            raise Exception(f"Error while creating table in PostgreSQL: {error.pgerror}") from error

    def insert_results(self, results):
        """
        This method inserts the result from the object recognition to the database.

        Parameters
        ----------
        results : list
            List of dict's containing the following keys: `image_name`, `class`, `rel_x1`, `rel_y1`, `rel_x2`, `rel_y2`.

        """
        try:
            insert_query = f"INSERT INTO {self.table_name} (image_name, class, rel_x1, rel_y1, rel_x2, rel_y2) VALUES %s;"
            results_as_tuple = [(res["image_name"], res["class"], res["rel_x1"], res["rel_y1"], res["rel_x2"], res["rel_y2"]) for res in results]
            execute_values(self.cursor, insert_query, results_as_tuple)
        except psycopg2.Error as error:
            raise Exception(f"Error while inserting data to PostgreSQL: {error.pgerror}") from error

    def get_unique_images(self):
        """
        This method retrieves a list of unique images in the current session.

        Returns
        -------
        unique_images : list
            List of strings containing unique image names.

        """
        try:
            get_unique_images_query = f"SELECT DISTINCT image_name FROM {self.table_name};"
            self.cursor.execute(get_unique_images_query)
            unique_images = self.cursor.fetchall()
            unique_images = [image[0] for image in unique_images]
        except psycopg2.Error as error:
            raise Exception(f"Error while getting unique images from PostgreSQL: {error.pgerror}") from error

        return unique_images

    def get_objects_of_image(self, image_name):
        """
        This method retrieves the recognized objects from the database belonging to the provided image.

        Parameters
        ----------
        image_name : str
            Name of the image of which the objects should be retrieved.

        Returns
        -------
        objects_of_image : list
            List of dicts containing the follwing keys: `id`, `type`, `bbox_dims`. `bbox_dims` contains the relative coordinates
            of the top left and bottom right corners of the bounding box.

        """

        try:
            get_objects_query = f"SELECT * FROM {self.table_name} WHERE image_name='{image_name}'"
            self.cursor.execute(get_objects_query)
            rows = self.cursor.fetchall()

            # Get column names and later retrieve values by name so we don't depend on magic indices
            col_names = [col.name for col in self.cursor.description]

            objects_of_image = [
                {
                    "id": row[col_names.index("id")],
                    "type": row[col_names.index("class")],
                    "bbox_dims": {
                        "x1": row[col_names.index("rel_x1")],
                        "y1": row[col_names.index("rel_y1")],
                        "x2": row[col_names.index("rel_x2")],
                        "y2": row[col_names.index("rel_y2")]
                    }
                } for row in rows
            ]
        except psycopg2.Error as error:
            raise Exception(f"Error while getting objects of image from PostgreSQL") from error

        return objects_of_image

    def close(self):
        """
        Closes the postgres connection.
        """
        try:
            self.cursor.close()
            self.connection.close()
            logger.info("PostgreSQL connection is closed")
        except psycopg2.Error as error:
            raise Exception(f"Error while closing PostgreSQL connection: {error.pgerror}") from error
