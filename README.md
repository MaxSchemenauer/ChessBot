# Chess Bot Project

Welcome to the **Chess Bot Project**! This project is a Python-based chess engine built using the `python-chess` library and `pygame` for rendering. It supports human vs. bot gameplay, bot vs. bot simulations, and various advanced features to analyze and visualize games. 

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Bot vs. Bot Simulations](#bot-vs-bot-simulations)
- [Code Structure](#code-structure)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

---

## Features
- **Play Against the Bot:** Test your skills against an AI opponent.
- **Bot vs. Bot Simulations:** Watch two versions of the bot compete to analyze their strategies.
- **Game Visualization:** Use the `simulation renderer` to visualize bot vs. bot games in real-time.
- **Advanced Move Handling:** Supports drag-and-drop and click-to-move functionality.
- **Legal Move Highlighting:** Displays valid moves for a selected piece (soon).
- **Logging and Analysis:** Tracks and logs game results, including timestamps and winning names/colors.

---

## 🛠 Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/MaxSchemenauer/ChessBot.git
   cd ChessBot
   ```

2. **Install the required libraries:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Required Python libraries:**
   - `pygame`
   - `python-chess`
   - `keyboard`  *(for input handling)*

---

## How to Play
- **Run the game:**
   ```bash
   python renderer.py
   ```
- **Controls:**
   - **Click-to-Move:** Click on a piece and then on a valid square.
   - **Drag-and-Drop:** Click and hold a piece to drag it, then release on a valid square.

---

## Bot vs. Bot Simulations
- **Run a simulation:**
   ```bash
   python simulate.py
   ```
- **Key Features:**
   - Uses a `Simulate` class to manage games between two bot versions.
   - Supports switching which bot goes first.
   - Logs results by bot names, not by color, for easier analysis.
   - Useful for testing improvements to the AI or comparing different strategies.

- **Visualize Simulations:**
   - Run the `simulation renderer` to watch bot games unfold in real-time.
   ```bash
   python simulation_renderer.py
   ```

---

## Code Structure
- **`renderer.py`** - Handles game rendering and user interactions.
- **`simulate.py`** - Manages bot vs. bot simulations and logs results.
- **`chessboard.py`** - Contains the `ChessBoard` class for managing game state.
- **`v3_minimax.py`** - The Engine - implements AI logic using Minimax with alpha-beta pruning.
- **`game.py`** - Coordinates input handling, move validation, and rendering.
- **`logs/`** - Stores simulation results with timestamps.

---

## Future Enhancements
- Improve bot’s defensive play, especially against early-game strategies like Scholar's Mate.
- Reward piece specific positioning at different points in the game.
- Implement zobrist hashing for efficient lookups
- Optimize the Minimax evaluation function for speed and efficiency.
- Implement opening book strategies for the bot.

---
