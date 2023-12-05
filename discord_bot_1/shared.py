from datetime import datetime
import random
import openai
import config as config
import re
import random
import bs4
import requests

name = "Aaron"
backstory = """Age: 28
Occupation: Real Estate Agent
Background: Aaron's insightful knowledge of the property market and his genuine approach make him a trusted advisor in real estate dealings."""

with open('bot_backstory.txt', 'r') as file:
    backstory = file.read()


async def respond_to_last(rds_c, rds_conn, client):
    """
    Responds to the last message from the database.

    Args:
    rds_c: Database cursor for executing queries.
    rds_conn: Database connection for committing changes.
    client: Discord client to interact with the Discord API.
    """

    try:
        # Retrieve the last 15 messages, including the most recent one
        rds_c.execute('SELECT * FROM chat_bots_verbose ORDER BY ROWID DESC LIMIT 15')
        last_messages = rds_c.fetchall()

        # Check if there are any messages
        if not last_messages:
            response_message = "No messages saved in the database!"
            await client.get_channel(config.studio_channel).send(response_message)
            rds_c.execute("""
            INSERT INTO chat_bots_verbose (message_id, author_id, content, channel_id, guild_id, timestamp, bot_name, bot_description) 
            VALUES (NULL, NULL, %s, %s, NULL, %s, %s, %s)
            """, (response_message, config.studio_channel, datetime.utcnow().isoformat(), name, backstory))
            rds_conn.commit()
            return

        # Extract the latest message details
        latest_message = last_messages[0]
        latest_message_id = latest_message[0]
        message_to_reply = latest_message[2]
        bot_name = latest_message[6]
        bot_description = latest_message[7]

        # Create a string of the last 15 messages for conversation context
        conversation = "\n\n".join([
            'You replied: ' + message[2] if message[6].lower() == name.lower() 
            else 'Message from ' + message[6] + ': ' + message[2] 
            for message in reversed(last_messages)
        ])

        # Generate a response based on the conversation and latest message
        response = await generate_ai_response(conversation, message_to_reply, bot_name, bot_description)

        # Send the response in the specified channel as a reply to the original message
        channel = client.get_channel(config.studio_channel)
        original_message = await channel.fetch_message(latest_message_id)
        message = await original_message.reply(remove_hashtags(response.strip('"')))

        # Insert the bot's response into the database
        rds_c.execute("""
        INSERT INTO chat_bots_verbose (message_id, author_id, content, channel_id, guild_id, timestamp, bot_name, bot_description) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (message.id, message.author.id, remove_hashtags(response.strip('"')), message.channel.id, message.guild.id, datetime.utcnow().isoformat(), name, backstory))
        rds_conn.commit()
    except Exception as e:
        print(e)


async def generate_ai_response(conversation, message_to_reply, bot_name, backstory):
    """
    Generates an AI response to a given message using OpenAI's GPT-3.5-turbo model.

    Args:
    conversation: String containing the conversation context.
    message_to_reply: The specific message to which the response is being generated.
    bot_name: Name of the bot that sent the message.
    backstory: Description or backstory of the bot.

    Returns:
    An AI-generated response based on the given message and context, 
    or an error message if an exception occurs.
    """

    try:
        # Set the OpenAI API key from the configuration
        openai.api_key = config.ai_key

        # Generate a random number for varying response lengths
        number = random.randint(75, 250)
        mood = 'happy'  # Define the mood for the response

        # Craft a detailed message prompt for the AI model
        message = (
            "Conversation so far for context:\n" +
            conversation + "\n\n" +
            "Description of who you are:\n" +
            backstory + "\n" +
            f"\nDescription of who you are replying to:\n" +
            f"From: {bot_name}\n" +
            f"Description of {bot_name}: {backstory}\n" +
            f"\nThis is the message sent by {bot_name} whom you are replying to:\n" +
            message_to_reply + 
            f"\n\nReply with a {mood} mood!\n" +
            "Reply in a human-like manner, keeping the response concise, contextually relevant, and emotionally appropriate.\n" + 
            "No hashtags."
        )
        
        print(message)

        # Generate a response using OpenAI's ChatCompletion API with the crafted message
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message}
            ],
            max_tokens=number  # Limit the response length to ensure conciseness
        )
        
        # Return the AI-generated response, stripping any leading/trailing whitespace
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Print any exceptions and return a default error message
        print(e)
        return "Sorry, I couldn't generate a response. Please try again later."


async def generate_ai_news(news):
    """
    Generates an AI response based on the latest news using OpenAI's GPT-3.5-turbo model.

    Args:
    news: A string containing the latest news to be discussed.

    Returns:
    An AI-generated message based on the given news, or an error message if an exception occurs.
    """

    try:
        # Set the OpenAI API key from the configuration
        openai.api_key = config.ai_key

        # Prepare a message prompt for the AI model
        # The message is crafted to simulate a discussion about the latest Minnesota news
        message = (
            f"Imagine you're diving into a discussion about the latest Minnesota news with a group of well-informed, open-minded individuals. " +
            f"As someone with this background: {backstory}, " +  # Ensure 'backstory' variable is defined in your context
            f"how would you bring up the following news in a friendly manner?\n\n" +
            f"News: {news}"
        )

        print(message)

        # Generate a response using OpenAI's ChatCompletion API with the crafted message
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the AI model
            messages=[
                    {"role": "user", "content": message}  # Define the user's role and content
            ]
        )
        # Return the AI-generated response, stripping any leading/trailing whitespace
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Print any exceptions and return a default error message
        print(e)
        return "Sorry, I couldn't generate a response. Please try again later."


async def chat(rds_c, rds_conn, client):
    try:
        # Retrieve the next bot's ID to speak
        next_bot = get_next_bot_to_speak(rds_c)
        print(next_bot)
        
        # Proceed if the current client's user ID matches the next bot's ID
        if client.user.id == next_bot:
            # Randomly decide whether to send news or respond to the last message
            if random.choice([False, False, False, True]):  
                # Fetch and process news
                news = await get_minnesota_news()
                ai_news = await generate_ai_news(news)
                # Send the news to the specified channel after removing hashtags
                message = await client.get_channel(config.studio_channel).send(content=remove_hashtags(ai_news.strip('"')))

                # Insert into 'chat_bots_verbose' with additional bot information
                rds_c.execute("""
                INSERT INTO chat_bots_verbose (message_id, author_id, content, channel_id, guild_id, timestamp, bot_name, bot_description) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (message.id, message.author.id, ai_news, message.channel.id, message.guild.id, datetime.utcnow().isoformat(), name, backstory))
                rds_conn.commit()
            else:
                # Respond to the last message if not sending news
                await respond_to_last(rds_c, rds_conn, client)

            # Update the timestamp for the bot
            update_bot_timestamp(rds_c, rds_conn, client.user.id)
    except Exception as e:
        print(e)


async def get_minnesota_news():
    URL = "https://news.google.com/search?q=minnesota&hl=en-US&gl=US&ceid=US:en"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    }
    response = requests.get(URL, headers=headers)
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    headlines = []

    # Depending on the structure of the page, you'll need to identify the tags and classes that contain the news.
    # The below selectors are examples and might not reflect the current structure of Google News.
    for article in soup.find_all('article', class_='MQsxIb xTewfe R7GTQ keNKEd j7vNaf Cc0Z5d VkAdve GU7x0c JMJvke q4atFc'):
        headline = article.a.text
        link = article.a['href']
        print(headline, link)

    # Print top 5 headlines as an example
    print("\nTop 5 Headlines:")

    for headline in soup.find_all('h3', class_='ipQwMb ekueJc RD0gLb'):
        print(headline.text)
        headlines.append(headline.text)
    
    # Return a random headline
    if headlines:
        return random.choice(headlines)
    else:
        return None
    

def get_next_bot_to_speak(c):
    """
    Retrieve the next bot to speak from the database.
    
    Args:
    c: Database cursor object for executing queries.

    Returns:
    The ID of the next bot to speak, or None if no entry is found.
    """

    # Execute SQL query to select the bot_id from the next_bot_to_speak table where id is 1
    c.execute("SELECT bot_id FROM next_bot_to_speak WHERE id = 1")
    bot_entry = c.fetchone()
    
    # Check if a result was found. If not, return None
    if not bot_entry:
        return None

    # Return the first element of the fetched row, which is the bot's ID
    return bot_entry[0]


def update_bot_timestamp(c, conn, bot_id):
    """
    Update the last spoken timestamp of a bot in the database.

    Args:
    c: Database cursor object for executing queries.
    conn: Database connection object to commit the changes.
    bot_id: The ID of the bot for which the timestamp is to be updated.
    """

    # Get the current time
    current_time = datetime.now()
    
    # Execute an SQL query to insert a new record into the bots table,
    # or update the last_spoken timestamp if the bot_id already exists
    c.execute("""
    INSERT INTO bots (bot_id, last_spoken) 
    VALUES (%s, %s)
    ON CONFLICT (bot_id) 
    DO UPDATE SET last_spoken = EXCLUDED.last_spoken
    """, (bot_id, current_time))
    
    # Commit the transaction to save the changes to the database
    conn.commit()


def remove_hashtags(text):
    """
    Remove hashtags from a given text string.

    Args:
    text: The text string from which hashtags are to be removed.

    Returns:
    The text string with hashtags removed.
    """

    # Use regular expression to substitute hashtags (denoted by '#') followed by any non-whitespace characters with an empty string
    return re.sub(r'#\S+', '', text)