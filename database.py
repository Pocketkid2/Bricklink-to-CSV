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
        self.logger.info("[DB] Connection established.")

    def _create_tables(self):
        """Create the necessary tables if they do not exist."""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bricklink_entries (
            element_id TEXT NOT NULL PRIMARY KEY,
            design_id TEXT NOT NULL,
            color_code TEXT NOT NULL
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS lego_store_entries (
            element_id TEXT NOT NULL PRIMARY KEY,
            lego_sells BOOLEAN NOT NULL,
            bestseller BOOLEAN,
            price REAL,
            max_order_quantity INTEGER
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bricklink_store_lots (
            store_id TEXT NOT NULL,
            lot_id TEXT NOT NULL,
            price REAL NOT NULL,
            design_id TEXT NOT NULL,
            color_code TEXT NOT NULL
        )''')

    def close(self):
        """Commit changes and close the database connection."""
        self.connection.commit()
        self.connection.close()
        self.logger.info("[DB] Connection closed.")

    def insert_bricklink_entry(self, element_id, design_id, color_code):
        """
        Insert a new entry into the BrickLink table.

        Args:
            element_id (str): The element ID.
            design_id (str): The design ID.
            color_code (str): The color code.
        """
        self.cursor.execute('INSERT OR IGNORE INTO bricklink_entries VALUES (?, ?, ?)', (element_id, design_id, color_code))
        if self.cursor.rowcount == 0:
            self.logger.info(f"[DB] Skipped existing BrickLink entry: {element_id}, {design_id}, {color_code}")
        else:
            self.logger.info(f"[DB] Inserted BrickLink entry: {element_id}, {design_id}, {color_code}")

    def insert_lego_store_entry(self, element_id, lego_sells, bestseller, price, max_order_quantity):
        """
        Insert a new entry into the LEGO Pick-a-Brick table.

        Args:
            element_id (str): The element ID.
            lego_sells (bool): Whether LEGO sells this item.
            bestseller (bool): Whether this item is a bestseller.
            price (str): The price of the item, in cents.
            max_order_quantity (int): The maximum order quantity.
        """
        if price is not None:
            price = float(price[1:])
        self.cursor.execute('INSERT OR IGNORE INTO lego_store_entries VALUES (?, ?, ?, ?, ?)', (element_id, lego_sells, bestseller, price, max_order_quantity))
        if self.cursor.rowcount == 0:
            self.logger.info(f"[DB] Skipped existing LEGO Pick-a-Brick entry: {element_id}, {lego_sells}, {bestseller}, {price}, {max_order_quantity}")
        else:
            self.logger.info(f"[DB] Inserted LEGO Pick-a-Brick entry: {element_id}, {lego_sells}, {bestseller}, {price}, {max_order_quantity}")

    def insert_bricklink_cart_entry(self, store_id, lot_id, price, design_id, color_code):
        """
        Insert a new entry into the BrickLink cart table.

        Args:
            store_id (str): The store ID.
            lot_id (str): The lot ID.
            price (float): The price of the item, in cents.
            design_id (str): The design ID.
            color_code (str): The color code.
        """
        self.cursor.execute('INSERT OR IGNORE INTO bricklink_store_lots VALUES (?, ?, ?, ?, ?)', (store_id, lot_id, price, design_id, color_code))
        if self.cursor.rowcount == 0:
            self.logger.info(f"[DB] Skipped existing BrickLink cart entry: {store_id}, {lot_id}, {price}, {design_id}, {color_code}")
        else:
            self.logger.info(f"[DB] Inserted BrickLink cart entry: {store_id}, {lot_id}, {price}, {design_id}, {color_code}")

    def get_bricklink_entry_by_design_id(self, design_id):
        """
        Retrieve a BrickLink entry by design ID.

        Args:
            design_id (int): The design ID.

        Returns:
            tuple: The row corresponding to the design ID, or None if not found.
        """
        self.cursor.execute('SELECT * FROM bricklink_entries WHERE design_id = ?', (design_id,))
        self.logger.info(f"[DB] Queried BrickLink entry by design ID: {design_id}")
        return self.cursor.fetchone()
    
    def get_bricklink_cart_entry_by_store_and_lot_id(self, store_id, lot_id):
        """
        Retrieve a BrickLink cart entry by store and lot ID.

        Args:
            store_id (int): The store ID.
            lot_id (int): The lot ID.

        Returns:
            tuple: The row corresponding to the store and lot ID, or None if not found.
        """
        self.cursor.execute('SELECT * FROM bricklink_store_lots WHERE store_id = ? AND lot_id = ?', (store_id, lot_id))
        self.logger.info(f"[DB] Queried BrickLink cart entry by store and lot ID: {store_id}, {lot_id}")
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
        self.logger.info(f"[DB] Queried BrickLink entry by design ID and color code: {design_id}, {color_code}")
        return self.cursor.fetchall()

    def get_lego_store_entry_by_element_id(self, element_id):
        """
        Retrieve a LEGO Pick-a-Brick entry by element ID.

        Args:
            element_id (int): The element ID.

        Returns:
            tuple: The row corresponding to the element ID, or None if not found.
        """
        self.cursor.execute('SELECT * FROM lego_store_entries WHERE element_id = ?', (element_id,))
        self.logger.info(f"[DB] Queried LEGO Pick-a-Brick entry by element ID: {element_id}")
        return self.cursor.fetchone()

    def get_bricklink_cart_entry_by_store_and_lot_id(self, store_id, lot_id):
        """
        Retrieve a BrickLink cart entry by store and lot ID.

        Args:
            store_id (int): The store ID.
            lot_id (int): The lot ID.

        Returns:
            tuple: The row corresponding to the store and lot ID, or None if not found.
        """
        self.cursor.execute('SELECT * FROM bricklink_store_lots WHERE store_id = ? AND lot_id = ?', (store_id, lot_id))
        self.logger.info(f"[DB] Queried BrickLink cart entry by store and lot ID: {store_id}, {lot_id}")
        return self.cursor.fetchone()
    
    def match_bricklink_entries_to_bricklink_cart_entries(self, store_id, lot_id):
        """
        Match BrickLink entries to BrickLink cart entries by store and lot ID.

        Args:
            store_id (str): The store ID.
            lot_id (str): The lot ID.

        Returns:
            tuple array: The matched rows, or an empty array if no matches are found.
        """
        self.cursor.execute('''
                            select element_id from bricklink_entries
                            join bricklink_store_lots
                            where bricklink_entries.design_id == bricklink_store_lots.design_id
                            and bricklink_entries.color_code == bricklink_store_lots.color_code
                            and bricklink_store_lots.store_id = ?
                            and bricklink_store_lots.lot_id = ?
                            ''', (store_id, lot_id))
        self.logger.info(f"[DB] Matched BrickLink entries to BrickLink cart entries by store and lot ID: {store_id}, {lot_id}")
        return self.cursor.fetchall()

    def match_bricklink_entries_to_lego_store_entries(self, design_id, color_code):
        """
        Match BrickLink entries to LEGO Pick-a-Brick entries by design ID and color code.

        Args:
            design_id (int): The design ID.
            color_code (int): The color code.

        Returns:
            tuple array: The matched rows, or an empty array if no matches are found.
        """
        self.cursor.execute('''
                            select * from bricklink_entries
                            inner join lego_store_entries
                            on bricklink_entries.element_id = lego_store_entries.element_id
                            where bricklink_entries.design_id = ?
                            and bricklink_entries.color_code = ?
                            ''', (design_id, color_code))
        self.logger.info(f"[DB] Matched BrickLink entries to LEGO Pick-a-Brick entries by design ID and color code: {design_id}, {color_code}")
        return self.cursor.fetchall()
    
    def compare_prices_for_lot(self, store_id, lot_id):
        """
        Compare prices between LEGO Pick-a-Brick and BrickLink.

        Returns:
            tuple array: The matched rows, or an empty array if no matches are found.
        """
        self.cursor.execute('''
                            select lse.element_id, lse.price as lego_price, bsl.price as bricklink_price
                            from lego_store_entries lse
                            join bricklink_entries be on lse.element_id == be.element_id
                            join bricklink_store_lots bsl on be.design_id == bsl.design_id and be.color_code == bsl.color_code
                            where bsl.store_id = ? and bsl.lot_id = ?
                            order by lse.element_id
                            ''', (store_id, lot_id))
        self.logger.info(f"[DB] Generated list to compare prices between LEGO Pick-a-Brick and BrickLink for store ID and lot ID: {store_id}, {lot_id}")
        return self.cursor.fetchall()
    
    def commit_changes(self):
        """Commit changes to the database."""
        self.connection.commit()
        self.logger.info("[DB] Committed changes.")

    def purge_bricklink_table(self):
        """Purge the BrickLink table."""
        self.cursor.execute('DROP TABLE bricklink_entries')
        self.logger.warning("[DB] Purged BrickLink table.")

    def purge_lego_store_table(self):
        """Purge the LEGO Pick-a-Brick table."""
        self.cursor.execute('DROP TABLE lego_store_entries')
        self.logger.warning("[DB] Purged LEGO Pick-a-Brick table.")

    def purge_bricklink_store_lots(self):
        """Purge the BrickLink store lots table."""
        self.cursor.execute('DELETE FROM bricklink_store_lots')
        self.logger.warning("[DB] Purged BrickLink store lots table.")
