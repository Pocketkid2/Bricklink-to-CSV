"""
Database.

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
        self.logger.info("Database connection established.")

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
            price INTEGER NOT NULL,
            max_order_quantity INTEGER NOT NULL
        )''')

    def close(self):
        """Commit changes and close the database connection."""
        self.connection.commit()
        self.connection.close()
        self.logger.info("Database connection closed.")

    def insert_bricklink_entry(self, element_id, design_id, color_code):
        """
        Insert a new entry into the BrickLink table.

        Args:
            element_id (int): The element ID.
            design_id (int): The design ID.
            color_code (int): The color code.
        """
        self.cursor.execute('INSERT OR IGNORE INTO bricklink_entries VALUES (?, ?, ?)', (element_id, design_id, color_code))
        if self.cursor.rowcount == 0:
            self.logger.info(f"Skipped existing BrickLink entry: {element_id}, {design_id}, {color_code}")
        else:
            self.logger.info(f"Inserted BrickLink entry: {element_id}, {design_id}, {color_code}")

    def insert_lego_pab_entry(self, element_id, lego_sells, bestseller, price, max_order_quantity):
        """
        Insert a new entry into the LEGO Pick-a-Brick table.

        Args:
            element_id (int): The element ID.
            lego_sells (bool): Whether LEGO sells this item.
            bestseller (bool): Whether this item is a bestseller.
            price (int): The price of the item, in cents.
            max_order_quantity (int): The maximum order quantity.
        """
        self.cursor.execute('INSERT OR IGNORE INTO lego_pab_entries VALUES (?, ?, ?, ?, ?)', (element_id, lego_sells, bestseller, price, max_order_quantity))
        if self.cursor.rowcount == 0:
            self.logger.info(f"Skipped existing LEGO Pick-a-Brick entry: {element_id}, {lego_sells}, {bestseller}, {price}, {max_order_quantity}")
        else:
            self.logger.info(f"Inserted LEGO Pick-a-Brick entry: {element_id}, {lego_sells}, {bestseller}, {price}, {max_order_quantity}")

    def get_bricklink_entry_by_design_id(self, design_id):
        """
        Retrieve a BrickLink entry by design ID.

        Args:
            design_id (int): The design ID.

        Returns:
            tuple: The row corresponding to the design ID, or None if not found.
        """
        self.cursor.execute('SELECT * FROM bricklink_entries WHERE design_id = ?', (design_id,))
        self.logger.info(f"Queried BrickLink entry by design ID: {design_id}")
        return self.cursor.fetchone()
    
    def get_bricklink_entries_by_design_id_and_color_code(self, design_id, color_code):
        """
        Retrieve a BrickLink entry by design ID and color code.

        Args:
            design_id (int): The design ID.
            color_code (int): The color code.

        Returns:
            tuple: The row corresponding to the design ID and color code, or None if not found.
        """
        self.cursor.execute('SELECT * FROM bricklink_entries WHERE design_id = ? AND color_code = ?', (design_id, color_code))
        self.logger.info(f"Queried BrickLink entry by design ID and color code: {design_id}, {color_code}")
        return self.cursor.fetchall()

    def get_lego_pab_entry_by_element_id(self, element_id):
        """
        Retrieve a LEGO Pick-a-Brick entry by element ID.

        Args:
            element_id (int): The element ID.

        Returns:
            tuple: The row corresponding to the element ID, or None if not found.
        """
        self.cursor.execute('SELECT * FROM lego_pab_entries WHERE element_id = ?', (element_id,))
        self.logger.info(f"Queried LEGO Pick-a-Brick entry by element ID: {element_id}")
        return self.cursor.fetchone()

    def purge_bricklink_table(self):
        """Purge the BrickLink table."""
        self.cursor.execute('DELETE FROM bricklink_entries')
        self.logger.warning("Purged BrickLink table.")

    def purge_lego_pab_table(self):
        """Purge the LEGO Pick-a-Brick table."""
        self.cursor.execute('DELETE FROM lego_pab_entries')
        self.logger.warning("Purged LEGO Pick-a-Brick table.")
