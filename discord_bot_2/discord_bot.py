# Import necessary libraries
import discord
from discord.ext import tasks
import psycopg2
import shared as shared
import config as config

# Set up Discord bot intents for enhanced functionality
intents = discord.Intents.default()
intents.message_content = True
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.guilds = True

# Initialize the Discord client with the specified intents
client = discord.Client(command_prefix=",", intents=intents)

print('establishing connection...')

# Establish a connection to the PostgreSQL database
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

# Event handler for when the bot is ready and online
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await client.wait_until_ready()
    await main.start()

# Background task loop running every 60 seconds
@tasks.loop(seconds=60)
async def main():
    try:
        # Call a shared function to perform chat operations
        await shared.chat(rds_c, rds_conn, client)
    except Exception as e:
        # Print any exceptions that occur during the execution of the task
        print(e) 

# Run the client with the specified token from the config
client.run(config.client_token)