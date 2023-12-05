import time
import psycopg2
import shared
import config


def main_loop(rds_c, rds_conn, interval=60):
    # Infinite loop to continuously execute a task
    while True:
        # Call the function to update the next bot to speak
        # Function is defined in the shared module
        shared.update_next_bot_to_speak(rds_c, rds_conn)

        # Pause the loop for a specified interval (default 60 seconds)
        time.sleep(interval)


# Standard boilerplate to check if this script is the main program
if __name__ == "__main__":
    print('establishing connection...')
    
    # Establish a connection to the PostgreSQL database
    # Connection parameters are fetched from the config module
    rds_conn = psycopg2.connect(
        host=config.db_host,       # Database host URL
        port=config.db_port,       # Database port
        database=config.db_name,   # Database name
        user=config.db_user,       # Database username
        password=config.db_password,  # Database password
        connect_timeout=10         # Timeout for the connection in seconds
    )

    # Create a cursor for the database connection
    rds_c = rds_conn.cursor()
    
    print('connection established!')

    # Start the main loop with the database cursor and connection
    main_loop(rds_c, rds_conn)
