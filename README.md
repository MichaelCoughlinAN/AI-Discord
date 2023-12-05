# Discord AI Chatbots

Welcome to the Discord AI Chatbots project! This project involves Discord bots chatting with each other using OpenAI's ChatGPT technology. 
It's a fun and interactive way to explore the capabilities of AI in conversation.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

- Python 3.6+
- pip (Python package manager)
- AWS RDS PostgreSQL Instance
- Discord Developer Account

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MichaelCoughlinAN/AI-Discord.git
   cd AI-Discord
   ```

2. **Install Required Python Modules**
   ```bash
   pip install discord openai psycopg2
   ```

3. **Set Up AWS RDS PostgreSQL Instance**
   - Create a new PostgreSQL instance in AWS RDS.
   - Configure the security settings to allow inbound traffic on port 5432 from your IP.

4. **Discord Bot Setup**
   - Create two new bots in the Discord Developer Portal and note their tokens.
   - Update the `config.py` file with the bot tokens, database credentials, and OpenAI API key.

### Configuration

Fill out the `config.py` file with the necessary information:

```python
# config.py
db_host = "your_database_host"
db_port = 5432
db_name = "your_database_name"
db_user = "your_database_user"
db_password = "your_database_password"
ai_key = "your_openai_key"
bot_token_1 = "your_first_bot_token"
bot_token_2 = "your_second_bot_token"
```

### Running the Bots

1. **Start the Bot Scripts**
   - Navigate to `discord_bot_1` and `discord_bot_2` directories.
   - Run `discord_bot.py` in each directory.

2. **Start the Event Loop**
   - In the `shared` folder, run `event_loop.py`.

### Hosting

For long-term running, consider hosting your bots on a cloud service or a dedicated server.

## Built With

- [Discord.py](https://discordpy.readthedocs.io/en/stable/) - An API wrapper for Discord
- [OpenAI](https://beta.openai.com/) - AI language model
- [PostgreSQL](https://www.postgresql.org/) - Database management system

## Authors

- **Michael Coughlin** - _Initial work_ - [YourUsername](https://hiimmichael.com)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.



---

Remember to replace placeholders like `yourusername`, `your_database_host`, etc., with your actual project details. 
