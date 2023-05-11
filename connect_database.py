"""
This module provides funcitonality to connect to database
"""

import sqlite3
import pandas as pd


class DatabaseOperation:
    """Connects to a database"""

    def __init__(self, database: str) -> None:
        self.conn = None
        self.cursor = None
        self.database = database

    def connect_to_db(self) -> None:
        """connects to db"""
        try:
            self.conn = sqlite3.connect(self.database)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as ex:
            print(ex)

    def close_connection(self) -> None:
        """closes connection"""
        if self.conn:
            self.conn.close()

    def create_table(self) -> None:
        """execute sql query for create, update, delete, insert

        Args:
            query (str): query for create, update, delete or insert
        """
        query = """
            CREATE TABLE IF NOT EXISTS Movies( 
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                movie_name TEXT NOT NULL, 
                tomatometer_score TEXT, 
                audience_score TEXT, 
                tomatometer_state TEXT,
                storyline TEXT, 
                rating TEXT, 
                genres TEXT, 
                review_1 TEXT, 
                review_2 TEXT, 
                review_3 TEXT, 
                review_4 TEXT,  
                review_5 TEXT, 
                status TEXT NOT NULL);
            """
        self.cursor.execute(query)
        self.conn.commit()

    def insert_excel_to_database(self, data: pd.DataFrame) -> None:
        """insert data generated from excel to database

        Args:
            file_path (str): path to excel file
        """
        data.to_sql("Movies", self.conn, if_exists="append", index=False)
        
    def perform_op(self, data) -> None:
        """perform databse operation CREATE UPDATE INSERT and DELETE ONLY

        Args:
            data (dataframe): data frame to inserted
        """
        self.connect_to_db()
        self.create_table()
        self.insert_excel_to_database(data)
        self.close_connection()
