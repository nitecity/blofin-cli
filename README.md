## Interact With Your Account Via Terminal

### This script only works with [Blofin Exchange](https://blofin.com)
#### Use this script and you don't have to login to your account everytime!

1. Prerequisites:
    - Creat your API Keys here: [Blofin](https://blofin.com/account/apis)
    - Install [Python](https://www.python.org/downloads/)
    - Open Terminal and Install ``dotenv`` package:<br><br>
        ```
          pip install python-dotenv
          pip install requests
        ```
2. Download The Repo:

    ```
      git clone https://github.com/nitecity/blofin-cli
      cd blofin-cli
    ```

3. Run the script:
    <p>Windows</p>

   ```
       py main.py
   ```
   <p>Mac and Linux</p>

   ```
       python3 main.py
   ```

4. After storing your API Keys, You'll see these options:

    <img width="689" alt="trade" src="https://github.com/user-attachments/assets/351729fc-440c-4426-b7e1-cafb970b2edf" />

5. Let's place a limit order

    <img width="562" alt="examp" src="https://github.com/user-attachments/assets/106aec56-8eb4-4b80-8c1f-526a675028b3" />


  

*Just one thing! When you're going to set your order size, you have to enter the quantity of the contract.<br>*
*Exmple: For Bitcoin, each contract worth 0.001 $BTC and minimum size must be equal or more than "0.1"<br>*
*To see other tickers info, Click Here: [Contracts Info](https://openapi.blofin.com/api/v1/market/instruments)<br>*

