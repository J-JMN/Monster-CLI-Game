<pre>
    ███╗   ███╗ ██████╗ ███╗   ██╗███████╗████████╗███████╗██████╗
    ████╗ ████║██╔═══██╗████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗
    ██╔████╔██║██║   ██║██╔██╗ ██║███████╗   ██║   █████╗  ██████╔╝
    ██║╚██╔╝██║██║   ██║██║╚██╗██║╚════██║   ██║   ██╔══╝  ██╔══██╗
    ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║███████║   ██║   ███████╗██║  ██║
    ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝</pre>

# Monster World CLI Game

A captivating command-line interface monster-collecting and battling game built with Python, SQLAlchemy, and Rich. Embark on an adventure, catch powerful monsters, challenge other players, and climb the global leaderboard!

## Table of Contents

* [Description](#description)

* [Features](#features)

* [How to Run](#how-to-run)

* [Technologies Used](#technologies-used)

## Description

Monster World is a text-based adventure where players can register, collect unique monsters, engage in dynamic turn-based battles against wild creatures or other players, trade monsters, and track their progress through an integrated achievement system and global leaderboard. The game leverages `Rich` for a vibrant and engaging command-line interface.

## Features

* **Player Management:**

  * Secure login and registration system.

  * View player profile with level, experience, and money.

  * Player experience and leveling system with an interactive XP bar.

* **Monster Collection:**

  * Discover and catch wild monsters with varying rarities and catch chances.

  * Manage and view your collection of owned monsters, displaying their stats and types.

  * Monsters gain experience and level up.

* **Battle Systems:**

  * **Player vs. Environment (PvE):** Engage in turn-based battles against wild monsters.

  * **Player vs. Player (PvP):** Challenge other registered players in strategic monster battles.

  * Dynamic combat display with Rich library.

  * Type effectiveness system for strategic gameplay.

  * Monsters heal and level up post-victory.

* **Reward Systems:**

  * **Achievement System:** Unlock various achievements for milestones (e.g., "First Catch", "First Win", "Collector"). Achievements grant money and XP rewards.

  * **Global Leaderboard:** See how you rank against all other players based on level and experience.

* **Economy & Utility:**

  * Earn money from battles.

  * Trade monsters with other players.

  * Heal injured monsters at the Healing Shrine.

* **Rich CLI Experience:**

  * Utilizes the `Rich` library for beautifully formatted tables, panels, and animated feedback.

## How to Run

To get this game up and running on your local machine:

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/J-JMN/Monster-CLI-Game.git](https://github.com/J-JMN/Monster-CLI-Game.git)
   cd Monster-CLI-Game
   ```

2. **Set up a virtual environment (recommended):**

   ```bash
   pipenv install
   pipenv shell
   ```


3. **Run the game:**

   ```bash
   python cli.py
   ```

## Technologies Used

* **Python 3:** The core programming language.

* **SQLAlchemy:** ORM (Object Relational Mapper) for database interactions with SQLite.

* **Rich:** A Python library for rich text and beautiful formatting in the terminal.

* **SQLite:** A lightweight, file-based database for persistence.

## License

This project is licensed under the MIT License 
