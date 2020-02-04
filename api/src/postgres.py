import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv


class Postgres:
    def open(self):
        try:
            self.connection = psycopg2.connect(
                user = os.getenv("DB_USER"),
                password = os.getenv("DB_PASSWORD"),
                host = os.getenv("DB_HOST"),
                port = os.getenv("DB_PORT"),
                database = os.getenv("DB_NAME")
            )
            self.connection.autocommit = True

            self.cursor = self.connection.cursor()

        except (Exception, psycopg2.Error) as error:
            print ("Error while connecting to PostgreSQL", error)

    def create_table(self, table_name="sorterbot"):
        check_table_query = f"SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='{table_name}');"
        self.cursor.execute(check_table_query)
        table_exists = self.cursor.fetchone()[0]
        
        if table_exists:
            print(f"Table '{table_name}' already exists, skipping table creation...")
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

    def insert_results(self, results, table_name="sorterbot"):
        insert_query = f"INSERT INTO {table_name} (img_name, class, rel_x1, rel_y1, rel_x2, rel_y2) VALUES %s;"
        execute_values(self.cursor, insert_query, results)

    def close(self):
        self.cursor.close()
        self.connection.close()
        print("PostgreSQL connection is closed")