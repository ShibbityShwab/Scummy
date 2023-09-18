# SCUM Discord Integration and Log Parser

This repository provides a suite of two Python scripts: 
1. A Discord bot that posts game-related updates in real-time to a designated Discord channel.
2. A script that fetches and parses SCUM game logs for various player activities.

## Features
1. **scummyDiscord.py**: This script defines a Discord bot that connects to a MySQL database to fetch new player death records and post them to a designated Discord channel.
2. **scummyLogs.py**: This script pulls game logs over FTP, parses different player activities like logins, logouts, chat messages, deaths, etc., and saves them to a MySQL database.

## Setup

### Prerequisites:
- You need to have `discord.py` and `mysql-connector-python` installed:
    ```bash
    pip install discord.py mysql-connector-python
    ```

### Configuration:
- Replace database connection details and FTP details with your own credentials.
- Ensure the necessary tables (`RunLog`, `Login`, `Logout`, `Death`, etc.) exist in your database.

### Running the Scripts:
1. Run `scummyDiscord.py` to start the Discord bot.
2. Run `scummyLogs.py` to start the log fetcher and parser.

## Note:
Never commit or share scripts with sensitive information like database or bot token credentials. Always use environment variables or config files to handle such details securely.

## License
This project is open-sourced under the [MIT License](https://opensource.org/licenses/MIT).

## Contributions
Contributions are welcome! Please make sure to test your changes before making a pull request.
