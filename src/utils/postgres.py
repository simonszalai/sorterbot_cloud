import os
from utils.logger import logger
import psycopg2
from psycopg2.extras import execute_values


class Postgres:
    def open(self):
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

        except (Exception, psycopg2.Error) as error:
            logger.error("Error while connecting to PostgreSQL", error)

    def create_table(self, table_name="sorterbot"):
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
                img_name TEXT,
                class TEXT,
                rel_x1 TEXT,
                rel_y1 TEXT,
                rel_x2 TEXT,
                rel_y2 TEXT
            );
        """

        self.cursor.execute(create_table_query)

    def insert_results(self, results):
        insert_query = f"INSERT INTO {self.table_name} (img_name, class, rel_x1, rel_y1, rel_x2, rel_y2) VALUES %s;"
        execute_values(self.cursor, insert_query, results)

    def get_unique_images(self):
        get_unique_images_query = f"SELECT DISTINCT img_name FROM {self.table_name};"
        self.cursor.execute(get_unique_images_query)
        unique_images = self.cursor.fetchall()
        return [image[0] for image in unique_images]

    def get_objects_of_image(self, image_name):
        get_objects_query = f"SELECT * FROM {self.table_name} WHERE img_name='{image_name}'"
        self.cursor.execute(get_objects_query)
        rows = self.cursor.fetchall()

        # Get column names and later retrieve values by name so we don't depend on magic indices
        col_names = [col.name for col in self.cursor.description]

        return [
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

    def close(self):
        self.cursor.close()
        self.connection.close()
        logger.info("PostgreSQL connection is closed")
