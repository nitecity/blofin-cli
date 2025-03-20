## Interact With Your Account Via Terminal

### This script works with [Blofin Exchange](https://blofin.com)

1. Prerequisites:
  - Creat your API Key here: [Blofin](https://blofin.com/account/apis)
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
4. After storing your API Keys, You'll see these options:

    <img width="689" alt="trade" src="https://github.com/user-attachments/assets/351729fc-440c-4426-b7e1-cafb970b2edf" />

5. Let's place a limit order

    <img width="562" alt="examp" src="https://github.com/user-attachments/assets/106aec56-8eb4-4b80-8c1f-526a675028b3" />


  

*Just one thing! If you want to set the size of your order, you have to enter the quantity of the ticker contracts*<br>
*Exmple: For Bitcoin, each contract worth 0.001 $BTC and minimum size must be equal or more than "0.1"*<br>
*To see other tickers info, go to this URL: [Contracts Info](https://openapi.blofin.com/api/v1/market/instruments?instId=btc-usdt")<br>

