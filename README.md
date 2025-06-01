## Blofin-CLI: Trade on Blofin Exchange from Your Terminal

Blofin-CLI is a powerful and convenient command-line tool that allows you to interact with your [Blofin Exchange](https://blofin.com) trading account directly from your terminal. Place and cancel orders, view your open positions and pending orders, and close positions with ease.

### Key Features:

  * **Place Orders:** Quickly execute market and limit orders.
  * **Cancel Orders:** Cancel pending orders.
  * **Position Management:** Get a clear overview of your open and pending orders, and close open positions.

### Prerequisites

Before you begin, you will need the following:

  * A [Blofin Exchange](https://blofin.com) account.
  * API Keys from your Blofin account. You can create them [here](https://blofin.com/account/apis).
  * [Python 3](https://www.python.org/downloads/) installed on your system.
  * The following Python packages: `python-dotenv`, `requests`, and `colorama`.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/nitecity/blofin-cli
    cd blofin-cli
    ```

2.  **Install the required packages:**

    ```bash
    pip install python-dotenv requests colorama
    ```

### Configuration

The first time you run the script, you will be prompted to enter your Blofin API Key, Secret Key, and Passphrase. This information will be securely stored in a `.env` file in the project directory for future use.

<img width="1000" alt="API Key Setup" src="./imgs/api.png" />

### Usage

Run the script from your terminal:

  * **Windows:**

    ```bash
    py main.py
    ```

  * **macOS and Linux:**

    ```bash
    python3 main.py
    ```

Once the script is running, you will see a menu of available options:

<img width="700" alt="Main Menu" src="./imgs/1.png" />

**Placing a Limit Order:**

To place a limit order, select the appropriate option from the menu and follow the prompts to enter the required information, such as the trading pair, order side, size, and price.

<img width="700" alt="Placing a Limit Order" src="./imgs/2.png" />
<img width="700" alt="Limit Order Confirmation" src="./imgs/3.png" />

### Disclaimer

***NOTE:*** The Take Profit (TP) and Stop Loss (SL) calculations are approximate. This tool is provided as-is, and the user assumes all risk associated with its use.