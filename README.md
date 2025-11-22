# FlashLoan Arbitrage Bot

A Python script to automate arbitrage opportunities between decentralized exchanges (DEXs) on the Ethereum network using flash loans. This script requires zero initial capital as it borrows funds, executes the trade, and repays the loan within a single transaction.

This bot is provided for educational purposes to demonstrate the logic behind flash loan arbitrage. The crypto market is highly volatile and profitable opportunities are rare and often competed away by bots with lower latency. **Use at your own risk. You are responsible for any financial loss.**

## Features

- Monitors price feeds from Uniswap V2 and Sushiswap.
- Calculates potential profit after accounting for gas fees and DEX fees.
- Executes a flash loan via Aave protocol if a profitable opportunity is found.
- Automatically handles loan repayment.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/CyberProtons/FlashLoan-Arbitrage-Bot.git
    cd FlashLoan-Arbitrage-Bot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    - Create a `.env` file in the same directory.
    - Copy the contents of `.env.example` into your `.env` file.
    - Fill in your `PRIVATE_KEY` and `INFURA_PROJECT_ID`.
    - **NEVER** commit your `.env` file to a public repository.

4.  **Run the bot:**
    ```bash
    python main.py
    ```

## How it Works

The bot runs in a loop, performing the following steps:
1. Fetches the price of a target token (e.g., WETH) on Uniswap and Sushiswap.
2. Calculates the spread and potential profit.
3. If profit is positive and exceeds a minimum threshold, it prepares a flash loan transaction.
4. If no profitable opportunity is found, it performs a "wallet dust cleanup" to ensure smooth operation for future runs.
