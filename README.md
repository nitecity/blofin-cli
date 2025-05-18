## Interact With Your Trading Account Via Terminal

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

    <img width="689" alt="examp1" src="./imgs/1.png" />

5. Let's place a limit order
    <p><i>Look at the inputs</i></p>
    <img width="562" alt="examp2" src="./imgs/2.png" />
    <img width="562" alt="examp3" src="./imgs/3.png" />

<p><i>TP-SL calculation is approximate</i></p>
