"""
Utility class to provide methods to interact with the PostgreSQL database.

"""

import os
import psycopg2
import traceback
import functools
from psycopg2 import pool
from psycopg2.extras import execute_values


def add_connection(func):
    """
    Decorator function to retrieve a connection from the connection pool, pass it to the decorated function,
    then put it back to the pool.

    """

    @functools.wraps(func)
    def add_conn_wrapper(self, *args, **kwargs):
        # Get connection from pool
        connection = self.postgres_pool.getconn()
        connection.autocommit = True
        kwargs["cursor"] = connection.cursor()
        # Call wrapper function and pass cursor
        value = func(self, *args, **kwargs)
        # Put back connection
        kwargs["cursor"].close()
        self.postgres_pool.putconn(connection)
        return value
    return add_conn_wrapper


class Postgres:
    """
    Class to provide method to interact with PostgreSQL database. Uses connection pooling to avoid opening and closing
    connections every time a request comes in. It uses a single database which is created when starting the service if
    it does not exist already. Each arm's data is saved to a separate schema while each session gets its own table.

    Parameters
    ----------
    db_name : str
        Name of the database to be used (and created at startup if needed).

    """

    def __init__(self, db_name="sorterbot"):
        try:
            # First connect to the default maintenance database
            connection = psycopg2.connect(os.getenv("PG_CONN"))
            connection.autocommit = True
            cursor = connection.cursor()

            # Check if a database exists with the provided name
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
            db_exists = cursor.fetchone()

            # Create the database if it doesn't exist
            if not db_exists:
                # logger.info(f"Database '{db_name}' does not exists, creating...")
                cursor.execute(f"CREATE DATABASE {db_name}")

            # Close connection to default database
            cursor.close()
            connection.close()

            # Create connection pool
            self.postgres_pool = pool.SimpleConnectionPool(1, 100, f"{os.getenv('PG_CONN')}/{db_name}")

        except psycopg2.Error as error:
            traceback.print_exc()
            raise Exception(f"Error while connecting to PostgreSQL: {error}") from error

    @add_connection
    def create_table(self, cursor, schema_name, table_name):
        """
        This method creates a new table with a given name in the database if it does not exist yet. A separate
        table should be created for each session.

        Parameters
        ----------
        cursor : psycopg2.cursor
            Cursor to be used for SQL execution. Provided by `add_connection` decorator.
        schema_name : str
            Name of the schema to be created. Corresponds to arm_id.
        table_name : str
            Name of the table to be created. Corresponds to session_id.

        Returns
        -------
        table_created : bool
            True if table was created, false if it already existed.

        """

        try:
            # Since postgres converts table names to lowercase, this is needed to avoid unexpected behavior
            schema_name = schema_name.lower()
            table_name = table_name.lower()

            # Create schema if doesn't exist
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")

            # Create table if doesn't exist
            check_table_query = f"SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='{table_name}' AND table_schema='{schema_name}');"
            cursor.execute(check_table_query)
            table_exists = cursor.fetchone()[0]
            if table_exists:
                return False

            create_table_query = f"""
                CREATE TABLE {schema_name}.{table_name} (
                    id SERIAL PRIMARY KEY,
                    image_name TEXT,
                    image_width SMALLINT,
                    image_height SMALLINT,
                    class SMALLINT,
                    x1 SMALLINT,
                    y1 SMALLINT,
                    x2 SMALLINT,
                    y2 SMALLINT
                );
            """

            cursor.execute(create_table_query)

        except psycopg2.Error as error:
            traceback.print_exc()
            raise Exception(f"Error while creating table in PostgreSQL: {error}") from error

    @add_connection
    def insert_results(self, cursor, schema_name, table_name, results):
        """
        This method inserts the result from the object recognition to the database.

        Parameters
        ----------
        cursor : psycopg2.cursor
            Cursor to be used for SQL execution. Provided by `add_connection` decorator.
        schema_name : str
            Name of the schema to be used. Corresponds to arm_id.
        table_name : str
            Name of the table to be used. Corresponds to session_id.
        results : list
            List of dict's containing the following keys: `image_name`, `image_width`, `image_height`, `class`, `x1`, `y1`, `x2`, `y2`.

        """

        try:
            # Since postgres converts table names to lowercase, this is needed to avoid unexpected behavior
            schema_name = schema_name.lower()
            table_name = table_name.lower()

            insert_query = f"INSERT INTO {schema_name}.{table_name} (image_name, image_width, image_height, class, x1, y1, x2, y2) VALUES %s;"
            results_as_tuple = [(
                res["image_name"],
                int(res["image_width"]),
                int(res["image_height"]),
                int(res["class"]),
                int(res["x1"]),
                int(res["y1"]),
                int(res["x2"]),
                int(res["y2"])
            ) for res in results]
            execute_values(cursor, insert_query, results_as_tuple)

        except psycopg2.Error as error:
            exc = Exception(f"Error while inserting data to PostgreSQL: {error}")
            traceback.print_exc()
            raise exc from error

    @add_connection
    def get_unique_images(self, cursor, schema_name, table_name):
        """
        This method retrieves a list of unique images in the current session.

        Parameters
        ----------
        cursor : psycopg2.cursor
            Cursor to be used for SQL execution. Provided by `add_connection` decorator.
        schema_name : str
            Name of the schema to be used. Corresponds to arm_id.
        table_name : str
            Name of the table to be used. Corresponds to session_id.

        Returns
        -------
        unique_images : list
            List of strings containing unique image names.

        """

        try:
            # Since postgres converts table names to lowercase, this is needed to avoid unexpected behavior
            schema_name = schema_name.lower()
            table_name = table_name.lower()

            get_unique_images_query = f"SELECT DISTINCT image_name FROM {schema_name}.{table_name};"
            cursor.execute(get_unique_images_query)
            unique_images = cursor.fetchall()
            unique_images = [image[0] for image in unique_images]

        except psycopg2.Error as error:
            traceback.print_exc()
            raise Exception(f"Error while getting unique images from PostgreSQL: {error}") from error

        return unique_images

    @add_connection
    def get_objects_of_image(self, cursor, schema_name, table_name, image_name):
        """
        This method retrieves the recognized objects from the database belonging to the provided image.

        Parameters
        ----------
        cursor : psycopg2.cursor
            Cursor to be used for SQL execution. Provided by `add_connection` decorator.
        schema_name : str
            Name of the schema to be used. Corresponds to arm_id.
        table_name : str
            Name of the table to be used. Corresponds to session_id.
        image_name : str
            Name of the image of which the objects should be retrieved.

        Returns
        -------
        objects_of_image : list
            List of dicts containing the follwing keys: `id`, `type`, `bbox_dims`. `bbox_dims` contains the relative coordinates
            of the top left and bottom right corners of the bounding box.

        """

        try:
            # Since postgres converts table names to lowercase, this is needed to avoid unexpected behavior
            schema_name = schema_name.lower()
            table_name = table_name.lower()

            get_objects_query = f"SELECT * FROM {schema_name}.{table_name} WHERE image_name='{image_name}'"
            cursor.execute(get_objects_query)
            rows = cursor.fetchall()

            # Get column names and later retrieve values by name so we don't depend on magic indices
            col_names = [col.name for col in cursor.description]

            objects_of_image = [
                {
                    "id": row[col_names.index("id")],
                    "class": row[col_names.index("class")],
                    "img_dims": (row[col_names.index("image_width")], row[col_names.index("image_height")]),
                    "bbox_dims": {
                        "x1": row[col_names.index("x1")],
                        "y1": row[col_names.index("y1")],
                        "x2": row[col_names.index("x2")],
                        "y2": row[col_names.index("y2")]
                    }
                } for row in rows
            ]

        except psycopg2.Error as error:
            traceback.print_exc()
            raise Exception(f"Error while getting objects of image from PostgreSQL: {error}") from error

        return objects_of_image
