## Interact With Your Account Via Terminal

### This script works with [Blofin Exchange](https://blofin.com)

1. Prerequisites:
  - Creat your API Key from [Blofin](https://blofin.com/account/apis)
  - Install [Python](https://www.python.org/downloads/)
  - Open Terminal and Install ``dotenv`` package:

    ```
      pip install python-dotenv
    ```
2. Download The Repo:

    ```
      git clone https://github.com/nitecity/blofin-cli
      cd blofin-cli
    ```

3. Run `main.py`
4. You'll see these options:

    <img width="687" alt="trade" src="https://github.com/user-attachments/assets/bd8b8188-18fa-4d4d-b382-89a1011b6883" />

5. Interact with your account!
     Let's place a limit order<br>
    <img width="723" alt="examp" src="https://github.com/user-attachments/assets/88b925ce-7f47-4f1f-aa3a-c5878d16f3bc" />

  

*Just one thing! If you want to set the size of your order, you have to enter the quantity of the ticker contracts*<br>
*Exmple: For Bitcoin, each contract worth 0.001 $BTC and minimum size must be equal or more than "0.1"*<br>
*To see other tickers info, go to this URL: [Contracts Info](https://openapi.blofin.com/api/v1/market/instruments?instId=btc-usdt")<br>

