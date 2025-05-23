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
    print('***********************************************************')
    print('\nLet\'s get started!')
    print('\nPick One of The Options Below:\n')

    try:
        prompt = input("1. Place Order\n2. Pending Orders\n3. Open Positions\n4. Cancel Order\n5. Close Position\n6. Get Leverage\n7. Set Leverage\n8. Get Margin Mode\n9. Set Margin Mode\n10. Print API Credentials\n11. Modify API Credentials\n12. Get Balance\n13. Trade History\n14. Info About Size\n0. Exit\n\n> ")
    except:
        print("\nOperation cancelled by user")
        return
    if prompt == '0':
        return
    if prompt == "1":
        try:
            valid_inputs = ['1', '2', '3', '4']
            price = None

            symbol = input('Enter Symbol\nExample: [btc] | [eth]\n> ').upper().strip()
            b = Blofin(symbol+"-USDT")
            if not b.get_market_price()[1]:
                print("Invalid Symbol")
                return
            order_type = input("Order Type:\n1. limit\n2. market\n3. trigger\n4. post_only\n> ").lower().strip()
            if not order_type in valid_inputs:
                print('Invalid Input')
                return
            position_side = input("Position Side:\n1. long\n2. short\n> ").lower().strip()
            if not position_side in valid_inputs[:2]:
                print('Invalid Input')
                return
            size = input('Size (%): Example: [100] means "100%" of your balance\n> ').strip()
            try:
                size = float(size)
                if size < 1 or size > 100:
                    print('Size Must be 1-100')
                    return
            except ValueError:
                print("Size is mandatory and must be digit")
                return
            price = input("Price:\n> ").lower().strip() if not order_type == '2' else print("Order Type: market")
            try:
                if order_type != '2':
                    price = float(price)
                    if price <= 0:
                        print("Price Must be greater than 0")
                        return
            except ValueError:
                print("Price is mandatory and must be digit")
                return
            tp = input("TP: (Optional)\n> ").strip()
            try:
                if tp:
                    tp = float(tp)
                    if tp <= 0:
                        print("TP Must be greater than 0")
                        return
            except ValueError:
                print("TP must be digit")
                return
            sl = input("SL: (Optional)\n> ").strip()
            try:
                if sl:
                    sl = float(sl)
                    if sl <= 0:
                        print("SL Must be greater than 0")
                        return
            except ValueError:
                print("SL must be digit")
                return
        except:
            print("\nOperation cancelled by user")
            return

        print('Please Wait...\n')

        if position_side == '1':
            position_side = 'long'
        else:
            position_side = 'short'
        
        order_type_map = {
            '1': 'limit',
            '2': 'market',
            '3': 'trigger',
            '4': 'post_only'
        }
        order_type = order_type_map.get(order_type)

        [size_in_contract, markPrice, size_with_leverage, lvg] = b.calculate_size(size, position_side, order_type, price)

        cal_tp = None
        cal_sl = None
        tp_in_usdt = None
        sl_in_usdt = None
        long_tp_sl = lambda x,y: round(((x - y) / y) * 100 , 2)
        short_tp_sl = lambda y,x: round(((y - x) / y) * 100 , 2)
        # long
        if position_side == "long":
            if price and tp and sl:
                cal_tp = long_tp_sl(tp, price)
                cal_sl = long_tp_sl(sl, price)
            elif price and tp:
                cal_tp = long_tp_sl(tp, price)
            elif price and sl:
                cal_sl = long_tp_sl(sl, price)
            elif tp and sl:
                cal_tp = long_tp_sl(tp, markPrice)
                cal_sl = long_tp_sl(sl, markPrice)
            elif tp:
                cal_tp = long_tp_sl(tp, markPrice)
            elif sl:
                cal_sl = long_tp_sl(sl, markPrice)
        # short
        else:
            if price and tp and sl:
                cal_tp = short_tp_sl(price, tp)
                cal_sl = short_tp_sl(price, sl)
            elif price and tp:
                cal_tp = short_tp_sl(price, tp)
            elif price and sl:
                cal_sl = short_tp_sl(price, sl)
            elif tp and sl:
                cal_tp = short_tp_sl(markPrice, tp)
                cal_sl = short_tp_sl(markPrice, sl)
            elif tp:
                cal_tp = short_tp_sl(markPrice, tp)
            elif sl:
                cal_sl = short_tp_sl(markPrice, sl)

        if cal_tp:
            tp_in_usdt = round((size_with_leverage * cal_tp) / 100, 2)
        if cal_sl:
            sl_in_usdt = round((size_with_leverage * cal_sl) / 100 , 2)
            
        

        print("\nOrder Information:")
        print(f'\nPair:               "{symbol}-USDT"')
        print(f'Position Side:      "{position_side}"')
        print(f'Order type:         "{order_type}"')
        print(f'Leverage:           "{lvg}x"')
        print(f'Size with Leverage: "{size_with_leverage} USDT"')
        if order_type == "market":
            print(f'Price:              "{markPrice}"')
        else:
            print(f'Price:              "{price}"')
        if cal_tp:
            print(f'TP:                 "{tp}" => "{cal_tp}%" = "{tp_in_usdt} USDT"')
        if cal_sl:
            print(f'SL:                 "{sl}" => "{cal_sl}%" = "{sl_in_usdt} USDT"\n')
        

        try:
            sure = input("\nDo you confirm? [y/n]\n> ").lower().strip()
        except:
            print("\nOperation cancelled by user")
            return
        if sure == "no" or sure == "n":
            print('Ok, see you later!')
            return

        if position_side == 'long':
            if order_type == 'limit':
                b.place_normal_order("long", "buy", "limit", size_in_contract, tp, sl, price)
            elif order_type == "post_only":
                b.place_normal_order("long", "buy", "post_only", size_in_contract, tp, sl, price)
            elif order_type == 'market':
                b.place_normal_order("long", "buy", "market", size_in_contract, tp, sl)
            elif order_type == 'trigger':
                b.place_trigger_order("long", "buy", size_in_contract, tp, sl, price)
    
        if position_side == "short":
            if order_type == 'limit':
                b.place_normal_order("short", "sell", "limit", size_in_contract, tp, sl, price)
            elif order_type == "post_only":
                b.place_normal_order("short", "sell", "post_only", size_in_contract, tp, sl, price)
            elif order_type == 'market':
                b.place_normal_order("short", "sell", "market", size_in_contract, tp, sl)
            elif order_type == 'trigger':
                b.place_trigger_order("short", "sell", size_in_contract, tp, sl, price)

    elif prompt == "2":
        b = Blofin()
        b.get_open_trigger_orders()
        b.get_open_normal_orders()

    elif prompt == "3":

        b = Blofin()
        b.get_open_positions()

    elif prompt == "4":

        try:
            print("\nPending Order ID/Algo IDs:")
            with open(order_ids, 'r') as file:
                contents = file.read()
                print(contents)
            id = input("Enter ID (if you want to cancel more than one order, simpley use ',') e,g '61404050, 61391100'\n> ").strip()
            ids = id.split(',')
            for i in range(len(ids)):
                ids[i] = ids[i].strip()
                if not ids[i].isdigit():
                    print('Order Id is mandatory and must be digit')
                    return
                
        except:
            print("\nOperation cancelled by user")
            return

        b = Blofin()
        b.cancel_order(ids)

    elif prompt == "5":

        try:
            valid_inputs = ['1', '2']
            options = input("\n1. Close One Position\n2. Close All Positions\n> ")
            if not options in valid_inputs:
                print('Invalid Input')
                return
            
            if options == '1':
                symbol = input("\nEnter Symbol: e.g \"btc\"\n> ").upper().strip()
                position_side = input("Position Side:\n1. Long\n2. Short\n> ").strip()
                if not position_side in valid_inputs:
                    print('Invalid Input!')
                    return
                position_side_map = {
                    '1': 'long',
                    '2': 'short'
                }
                position_side = position_side_map.get(position_side)
                b = Blofin(symbol+"-USDT")
                b.close_position(position_side)
            else:
                b = Blofin()
                b.close_position(position_side='',isAll=True)
        except:
            print("\nOperation cancelled by user or something else went wrong!")
            return
        
        
    
    elif prompt == "6":

        try:
            symbol = input("\nEnter symbol(s):\nFor more than one, simply add ',' e,g. \"btc,eth\"\n> ").strip()
            symbols = symbol.split(',')
            for i in range(len(symbols)):
                symbols[i] = symbols[i].strip()
            modified_words = [element + '-usdt' for element in symbols]
            modified_symbols = ','.join(modified_words)
        except:
            print("\nOperation cancelled by user")
            return
        b = Blofin()
        b.get_leverage(modified_symbols)

    elif prompt == "7":

        try:
            valid_inputs = ['1', '2', '3']
            symbol = input("\nEnter Symbol: e.g \"btc\"\n> ").upper().strip()
            if not symbol:
                print('Symbol is mandatory')
                return
            leverage = input("Leverage:\n> ").strip()
            if not leverage or not leverage.isdigit():
                print('Leverage is mandatory and must be digit')
                return
            position_side = input("Position Side:\n1. Long\n2. Short\n3. Both\n> ").strip()
            if not position_side in valid_inputs:
                print('Invalid Input!')
                return
        except:
            print("\nOperation cancelled by user")
            return

        position_side_map = {
            '1': 'long',
            '2': 'short',
            '3': 'both'
        }
        position_side = position_side_map.get(position_side)
        b = Blofin(symbol+"-USDT")
        b.set_leverage(leverage, position_side)

    elif prompt == "8":

        b = Blofin()
        b.get_margin_mode()

    elif prompt == "9":

        try:
            valid_inputs = ['1', '2']
            marginMode = input("\nMargin Mode:\n1. Isolated\n2. Cross\n> ").strip()
            if not marginMode in valid_inputs:
                print('Invalid Input!')
                return
        except:
            print("\nOperation cancelled by user")
            return
        
        marginMode_map = {
            '1': 'isolated',
            '2': 'cross'
        }
        marginMode = marginMode_map.get(marginMode)
        b = Blofin()
        b.set_margin_mode(marginMode)

    elif prompt == "10":

        with open(envfile, 'r') as file:
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
            if not limit.isdigit():
                print('Limit value must be digit')
        except:
            print("\nOperation cancelled by user")
            return

        b = Blofin()
        kwargs = {}
        if symbol:
            kwargs['symbol'] = symbol
        if limit:
            kwargs['limit'] = limit
        b.get_trade_history(**kwargs)

    elif prompt == '14':

        b = Blofin()
        b.print_info()

    else:
        print("\nInvalid input! Enter a number between 1-14\n")


run()
