"""Database.

This module provides the DatabaseManager class for managing the SQLite cache
holding BrickLink and LEGO Pick-a-Brick data.
"""
import sqlite3


class DatabaseManager:
    """
    Manages the SQLite cache holding BrickLink and LEGO Pick-a-Brick data.

    Attributes:
        connection (sqlite3.Connection): The database connection.
        cursor (sqlite3.Cursor): The database cursor.
        logger (logging.Logger): The logger instance.
    """

    def __init__(self, database_filename, logger_instance):
        """
        Initialize the DatabaseManager with a database connection and logger.

        Args:
            database_filename (str): The filename of the SQLite database.
            logger_instance (logging.Logger): The logger instance.
        """
        self.connection = sqlite3.connect(database_filename)
        self.cursor = self.connection.cursor()
        self.logger = logger_instance
        self._create_tables()

    def _create_tables(self):
        """Create the necessary tables if they do not exist."""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bricklink_entries (
            element_id INTEGER NOT NULL PRIMARY KEY,
            design_id INTEGER NOT NULL,
            color_code INTEGER NOT NULL
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS lego_pab_entries (
            element_id INTEGER NOT NULL PRIMARY KEY,
            lego_sells BOOLEAN NOT NULL,
            bestseller BOOLEAN NOT NULL,
            price DECIMAL(10, 2) NOT NULL
        )''')

    def close(self):
        """Commit changes and close the database connection."""
        self.connection.commit()
        self.connection.close()

    def insert_bricklink_entry(self, element_id, design_id, color_code):
        """
        Insert a new entry into the BrickLink table.

        Args:
            element_id (int): The element ID.
            design_id (int): The design ID.
            color_code (int): The color code.
        """
        self.cursor.execute('INSERT INTO bricklink_entries VALUES (?, ?, ?)', (element_id, design_id, color_code))

    def insert_lego_pab_entry(self, element_id, lego_sells, bestseller, price):
        """
        Insert a new entry into the LEGO Pick-a-Brick table.

        Args:
            element_id (int): The element ID.
            lego_sells (bool): Whether LEGO sells this item.
            bestseller (bool): Whether this item is a bestseller.
            price (float): The price of the item.
        """
        self.cursor.execute('INSERT INTO lego_pab_entries VALUES (?, ?, ?, ?)', (element_id, lego_sells, bestseller, price))

    def get_bricklink_entry_by_design_id(self, design_id):
        """
        Retrieve a BrickLink entry by design ID.

        Args:
            design_id (int): The design ID.

        Returns:
            tuple: The row corresponding to the design ID, or None if not found.
        """
        self.cursor.execute('SELECT * FROM bricklink_entries WHERE design_id = ?', (design_id,))
        return self.cursor.fetchone()

    def get_lego_pab_entry_by_element_id(self, element_id):
        """
        Retrieve a LEGO Pick-a-Brick entry by element ID.

        Args:
            element_id (int): The element ID.

        Returns:
            tuple: The row corresponding to the element ID, or None if not found.
        """
        self.cursor.execute('SELECT * FROM lego_pab_entries WHERE element_id = ?', (element_id,))
        return self.cursor.fetchone()

    def purge_bricklink_table(self):
        """Purge the BrickLink table."""
        self.cursor.execute('DELETE FROM bricklink_entries')

    def purge_lego_pab_table(self):
        """Purge the LEGO Pick-a-Brick table."""
        self.cursor.execute('DELETE FROM lego_pab_entries')
