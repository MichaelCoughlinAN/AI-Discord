import random
import config as config


def insert_into_table(c, conn, table_name, data):
    """
    Inserts data into a specified table.

    Args:
    c: Database cursor for executing queries.
    conn: Database connection for committing changes.
    table_name: The name of the table to insert data into.
    data: Tuple containing the data to be inserted.
    """
    # Create placeholders for data insertion
    placeholders = ', '.join('?' * len(data))
    
    # Construct and execute the SQL query based on the table name
    if table_name == config.items_table:
        query = f"INSERT OR IGNORE INTO {table_name} VALUES (NULL, CURRENT_TIMESTAMP, {placeholders})"
    else:
        query = f"INSERT OR IGNORE INTO {table_name} VALUES (NULL, CURRENT_TIMESTAMP, FALSE, {placeholders})"
    
    c.execute(query, data)
    conn.commit()  # Commit the transaction


def drop_tables(c, conn):
    """
    Drops specified tables from the database.

    Args:
    c: Database cursor for executing queries.
    conn: Database connection for committing changes.
    """
    tables = ["table_name"]  # List of tables to be dropped
    for table in tables:
        c.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()  # Commit the transaction


def get_next_bot_to_speak(c):
    """
    Retrieves the ID of the next bot to speak from the database.

    Args:
    c: Database cursor for executing queries.

    Returns:
    The ID of the next bot to speak, or None if no entry is found.
    """
    c.execute("SELECT bot_id FROM next_bot_to_speak WHERE id = 1")
    bot_entry = c.fetchone()

    if not bot_entry:
        return None  # Return None if no bot entry is found

    return bot_entry[0]  # Return the bot's ID


def setup_tables(c, conn):
    """
    Sets up necessary tables in the database.

    Args:
    c: Database cursor for executing queries.
    conn: Database connection for committing changes.
    """
    # Alter existing tables to use BIGINT for bot_id
    c.execute('ALTER TABLE bots ALTER COLUMN bot_id TYPE BIGINT;')
    c.execute('ALTER TABLE next_bot_to_speak ALTER COLUMN bot_id TYPE BIGINT;')

    # Create 'bots' and 'next_bot_to_speak' tables if they don't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS bots (
            bot_id BIGINT PRIMARY KEY,
            last_spoken TIMESTAMP WITHOUT TIME ZONE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS next_bot_to_speak (
            id SERIAL PRIMARY KEY, 
            bot_id BIGINT
        )
    ''')
    conn.commit()

    # Insert a new record in 'next_bot_to_speak' if it's empty
    c.execute("SELECT * FROM next_bot_to_speak")
    if c.fetchone() is None:
        c.execute("INSERT INTO next_bot_to_speak (bot_id) VALUES (NULL)")
        conn.commit()

    # Create 'chat_bots_verbose' table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_bots_verbose (
            message_id BIGINT,
            author_id BIGINT,
            content TEXT,
            channel_id BIGINT,
            guild_id BIGINT,
            timestamp TIMESTAMP WITHOUT TIME ZONE,
            bot_name TEXT,
            bot_description TEXT,
            PRIMARY KEY (message_id)
        )
    ''')
    conn.commit()


def update_next_bot_to_speak(rds_c, rds_conn, N=3):
    """
    Updates the 'next_bot_to_speak' table with a randomly chosen bot from the top N bots.

    Args:
    rds_c: Database cursor for executing queries.
    rds_conn: Database connection for committing changes.
    N: Number of top bots to choose from. Default is 3.
    """
    # Select bot_id and last_spoken for all bots, ordered by last spoken time
    rds_c.execute("SELECT bot_id, last_spoken FROM bots ORDER BY last_spoken ASC")
    eligible_bots = rds_c.fetchall()

    if not eligible_bots:
        print('No bots...')
        return

    # Choose a random bot from the top N bots
    top_n_bots = eligible_bots[:N]
    chosen_bot = random.choice(top_n_bots)[0]

    # Update the 'next_bot_to_speak' table with the chosen bot
    rds_c.execute("UPDATE next_bot_to_speak SET bot_id = %s WHERE id = 1", (chosen_bot,))
    rds_conn.commit()

    print('Next bot to speak is ' + str(chosen_bot))
