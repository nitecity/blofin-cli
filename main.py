# BTC: 1 contract = 0.001 btc | ETH: 1 contract = 0.01 eth . 
# More information: https://openapi.blofin.com/api/v1/market/instruments?instId=op-usdt [This url shows information about OP. Feel free to change it]
import os
from dotenv import load_dotenv, set_key

def run():

    order_ids = 'order_ids.txt'
    envfile = '.env'
    if not os.path.isfile(envfile):
        try:
            api_key = input('API Key:\n> ').strip()
            secret = input('Secret Key:\n> ').strip()
            passphrase = input('Passphrase:\n> ').strip()
        except:
            print("\nOperation cancelled by user")
            return

        with open(envfile, 'w') as f:
            f.write(f'API_KEY="{api_key}"\n')
            f.write(f'SECRET="{secret}"\n')
            f.write(f'PASSPHRASE="{passphrase}"\n')

    from api import Blofin
    print('\n** Welcome **')
    print('You are going to interact with your account in "Blofin.com"')
    print('There is something you need to know about the size of your orders:')
    print('For BTC, "1" contract worth "0.001" $BTC | For ETH, "1" contract worth "0.01" $ETH')
    print('You have to enter a quantity of the contract in the "How Many Contracts?"')
    print('More information:')
    print('https://openapi.blofin.com/api/v1/market/instruments?instId=sol-usdt')
    print('[The url above, shows information about Solana. Feel free to change "sol-usdt" to any other pair]')
    print('***********************************************************************')
    print('\nLet\'s get started!')
    print('\nPick One of The Options Below:\n')

    try:
        prompt = input("1. Place Order\n2. Get pending Orders\n3. Get Open Positions\n4. Cancel Order\n5. Close Position\n6. Get Leverage\n7. Set Leverage\n8. Get Margin Mode\n9. Set Margin Mode\n10. Print API info\n11. Modify API info\n12. Get Balance\n13. Trade History\n\n> ")
    except:
        print("\nOperation cancelled by user")
        return

    if prompt == "1":
        try:
            symbol = input('Enter Symbol\nExample: [btc] | [eth]\n> ').upper().strip()
            side = input("[long] | [short]?\n> ").lower().strip()
            order_type = input("Order Type? [limit] | [market] | [trigger] | [post_only] | [fok] | [ioc]\n> ").lower().strip()
            size = input('How Many Contracts? Example: [1]\n> ').strip()
            entry = input("Price?\n> ").lower().strip() if not order_type == 'market' else print("Order Type = market")
            tp = input("TP: (Optional)\n> ").strip()
            sl = input("SL: (Optional)\n> ").strip()
        except:
            print("\nOperation cancelled by user")
            return

        print("\nOrder Information:")
        print(f'\nPair:          "{symbol}-USDT"')
        print(f'Position Side: "{side}"')
        print(f'Order type:    "{order_type}"')
        print(f'Contract(s):   "{size}"')
        if not order_type == "market":
            print(f'Price:         "{entry}"')
        print(f'TP:            "{tp}"')
        print(f'SL:            "{sl}"\n')
        try:
            sure = input("\nDo You Want to Continue?[y/n]\n> ").lower().strip()
        except:
            print("\nOperation cancelled by user")
            return
        if sure == "no" or sure == "n":
            return

        b = Blofin(symbol+"-USDT")

        if side == 'long':
            if order_type == 'limit':
                b.place_normal_order("long", "buy", "limit", size, tp, sl, entry)
            elif order_type == "post_only":
                b.place_normal_order("long", "buy", "post_only", size, tp, sl, entry)
            elif order_type == "fok":
                b.place_normal_order("long", "buy", "fok", size, tp, sl, entry)
            elif order_type == "ioc":
                b.place_normal_order("long", "buy", "ioc", size, tp, sl, entry)
            elif order_type == 'market':
                b.place_normal_order("long", "buy", "market", size, tp, sl)
            elif order_type == 'trigger':
                b.place_trigger_order("long", "buy", size, tp, sl, entry)
            else:
                print("Invalid Order Type")
                return
    
        if side == "short":
            if order_type == 'limit':
                b.place_normal_order("short", "sell", "limit", size, tp, sl, entry)
            elif order_type == "post_only":
                b.place_normal_order("short", "sell", "post_only", size, tp, sl, entry)
            elif order_type == "fok":
                b.place_normal_order("short", "sell", "fok", size, tp, sl, entry)
            elif order_type == "ioc":
                b.place_normal_order("short", "sell", "ioc", size, tp, sl, entry)
            elif order_type == 'market':
                b.place_normal_order("short", "sell", "market", size, tp, sl)
            elif order_type == 'trigger':
                b.place_trigger_order("short", "sell", size, tp, sl, entry)
            else:
                print("Invalid Order Type")
                return

    elif prompt == "2":

        try:
            isTrigger = input("\nLooking for Trigger/Algo Orders?[y/n]\n> ").lower().strip()
        except:
            print("\nOperation cancelled by user")
            return
        b = Blofin()
        if isTrigger == "y" or isTrigger == "yes":
            b.get_open_trigger_orders()
        else:
            b.get_open_normal_orders()

    elif prompt == "3":

        b = Blofin()
        b.get_open_positions()

    elif prompt == "4":

        try:
            print("\nPending Order or Algo IDs:")
            with open(order_ids, 'r') as file:
                contents = file.read()
                print(contents)
            order_type = input("\nOrder Type? [limit] | [trigger] | [post_only] | [fok] | [ioc]\n> ").lower().strip()
            id = input("Enter Order or Algo ID\n> ").strip()
        except:
            print("\nOperation cancelled by user")
            return
        b = Blofin()
        b.cancel_order(order_type, id)

    elif prompt == "5":

        try:
            symbol = input("\nEnter Symbol: e.g \"btc\"\n> ").upper().strip()
            positionSide = input("Position Side: [Long] | [Short]\n> ").lower().strip()
        except:
            print("\nOperation cancelled by user")
            return
        b = Blofin(symbol+"-USDT")
        b.close_position(positionSide)
    
    elif prompt == "6":

        try:
            symbols = input('\nEnter symbols:\n Example: "btc,eth"\n> ')
        except:
            print("\nOperation cancelled by user")
            return
        b = Blofin()
        b.get_leverage(symbols)

    elif prompt == "7":

        try:
            symbol = input("\nEnter Symbol: e.g \"btc\"\n> ").upper().strip()
            leverage = input("Leverage:\n> e.g. \"5\"").lower().strip()
            positionSide = input("Position Side: [Long] | [Short] | [Both]\n> ").lower().strip()
        except:
            print("\nOperation cancelled by user")
            return
        b = Blofin(symbol+"-USDT")
        b.set_leverage(leverage, positionSide)

    elif prompt == "8":

        b = Blofin()
        b.get_margin_mode()

    elif prompt == "9":

        try:
            marginMode = input("\nMargin Mode: [isolated] | [cross]\n> ").lower().strip()
        except:
            print("\nOperation cancelled by user")
            return
        b = Blofin()
        b.set_margin_mode(marginMode)

    elif prompt == "10":

        with open('.env', 'r') as file:
                contents = file.read()
                print(contents)

    elif prompt == "11":

        try:
            modify = input('\n1. Modify API Key\n2. Modify API Secret\n3. Modify Passphrase\n4. Modify All\n> ').strip()
        except:
            print('\nOperation cancelled by user')
            return
        
        if modify == "1":

            try:
                api_key = input('New API Key:\n> ').strip()
            except:
                print('\nOperation cancelled by user')
                return
            
            if api_key:
                load_dotenv(envfile)
                set_key(envfile, 'API_KEY', api_key)
                print('API Key Updated!')
            else:
                print("No input! No changes made!")

        elif modify == "2":

            try:
                api_secret = input('New API Secret:\n> ').strip()
            except:
                print('\nOperation cancelled by user')
                return

            if api_secret:
                load_dotenv(envfile)
                set_key(envfile, 'SECRET', api_secret)
                print('API Secret Updated')
            else:
                print('No input! No changes made!')

        elif modify == "3":

            try:
                passphrase = input('New Passphrase:\n> ').strip()
            except:
                print('\nOperation cancelled by user')
                return
            
            if passphrase:
                load_dotenv(envfile)
                set_key(envfile, 'PASSPHRASE', passphrase)
                print('Passphrase Updated!')
            else:
                print('No input! No changes made!')

        elif modify == "4":
                
            try:
                api_key = input('New API Key:\n> ').strip()
                api_secret = input('New API Secret:\n> ').strip()
                passphrase = input('New Passphrase:\n> ').strip()
            except:
                print('\nOperation cancelled by user')
                return

            if api_key and api_secret and passphrase:
                load_dotenv(envfile)
                set_key(envfile, 'API_KEY', api_key)
                set_key(envfile, 'SECRET', api_secret)
                set_key(envfile, 'PASSPHRASE', passphrase)
                print('API Key, Secret and Passphrase Updated!')
            else:
                print('One or more fields are empty. No changes made!')
        
        else:
            print('Invalid Option!')
    
    elif prompt == "12":

        b = Blofin()
        b.check_balance()

    elif prompt == "13":
        try:
            symbol = input('\nEnter symbol: [Default: All symbols]\n> ')
            limit = input('How many trades: [Default: 10]\n> ')
        except:
            print("\nOperation cancelled by user")
            return

        b = Blofin()
        if symbol and limit:
            b.get_trade_history(limit, symbol)
        elif symbol:
            b.get_trade_history(symbol=symbol)
        elif limit:
            b.get_trade_history(limit)
        else:
            b.get_trade_history()

    else:
        print("\nInvalid input! Enter a number between 1-13\n")


run()
