import sqlite3

# Global module variables
connection = None
cursor = None

# Set up database connection, create tables if they don't exist
def database_begin(database_filename):
    
    # Create connection and cursor
    global connection
    connection = sqlite3.connect(database_filename)

    global cursor
    cursor = connection.cursor()

    # Create tables if they don't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS bricklink_entries (
        element_id INTEGER NOT NULL PRIMARY KEY,
        design_id INTEGER NOT NULL,
        color_code INTEGER NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS lego_pab_entries (
        element_id INTEGER NOT NULL PRIMARY KEY,
        lego_sells BOOLEAN NOT NULL,
        bestseller BOOLEAN NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
    )''')


# Commit changes, close connection
def database_end():

    # Commit changes and close connection
    connection.commit()
    connection.close()


# Add a new bricklink entry to the database
def database_insert_bricklink_entry(element_id, design_id, color_code):

    # Insert entry into bricklink_entries table
    cursor.execute('INSERT INTO bricklink_entries VALUES (?, ?, ?)', (element_id, design_id, color_code))


# Add a new lego pick-a-brick (pab) entry to the database
def database_insert_lego_pab_entry(element_id, lego_sells, bestseller, price):


    # Insert entry into lego_pab_entries table
    cursor.execute('INSERT INTO lego_pab_entries VALUES (?, ?, ?, ?)', (element_id, lego_sells, bestseller, price))


# Get a bricklink entry by design_id
def database_get_bricklink_entry_by_design_id(design_id):
    
    # Check if design_id exists in bricklink_entries table
    cursor.execute('SELECT * FROM bricklink_entries WHERE design_id = ?', (design_id,))
    return cursor.fetchone()


# Get a lego pick-a-brick (pab) entry by element_id
def database_get_lego_pab_entry_by_element_id(element_id):
    
    # Check if element_id exists in lego_pab_entries table
    cursor.execute('SELECT * FROM lego_pab_entries WHERE element_id = ?', (element_id,))
    return cursor.fetchone()


# Clear all bricklink entries from the database
def database_clear_bricklink_entries():
    
    # Clear all entries from bricklink_entries table
    cursor.execute('DELETE FROM bricklink_entries')


# Clear all lego pick-a-brick (pab) entries from the database
def database_clear_lego_pab_entries():
    
    # Clear all entries from lego_pab_entries table
    cursor.execute('DELETE FROM lego_pab_entries')