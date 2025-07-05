# BTC: 1 contract = 0.001 btc | ETH: 1 contract = 0.01 eth . 
# More information: https://openapi.blofin.com/api/v1/market/instruments?instId=op-usdt [This url shows information about OP. Feel free to change it]
import os
from dotenv import load_dotenv, set_key
from api import Blofin
from colorama import Fore, Style, init

init()

# Colors
CYAN = Fore.CYAN
YELLOW = Fore.YELLOW
GREEN = Fore.GREEN
RED = Fore.RED
MAGENTA = Fore.MAGENTA
LIGHTBLUE_EX = Fore.LIGHTBLUE_EX
LIGHTRED_EX = Fore.LIGHTRED_EX
RESET = Style.RESET_ALL
BRIGHT = Style.BRIGHT

def run():

    envfile = '.env'
    if not os.path.isfile(envfile):
        try:
            print(f'{CYAN}\nBefore we get started, you need to provide the API credentials you got from https://blofin.com/account/apis{RESET}')
            api_key = input(f'{YELLOW}API Key:\n> {RESET}').strip()
            secret = input(f'{YELLOW}Secret Key:\n> {RESET}').strip()
            passphrase = input(f'{YELLOW}Passphrase:\n> {RESET}').strip()
        except:
            print(f"{RED}\nOperation cancelled by user{RESET}")
            return

        b = Blofin()
        isValid = b.API_auth(api_key, secret, passphrase)
        if isValid:
            with open(envfile, 'w') as f:
                f.write(f'API_KEY="{api_key}"\n')
                f.write(f'SECRET="{secret}"\n')
                f.write(f'PASSPHRASE="{passphrase}"\n')
            print(f'{GREEN}\n----------------------------------------{RESET}')
            print(f'{GREEN}\nProvided API data is valid{RESET}')
            print(f'{GREEN}Your API data has been stored in ".env"{RESET}')
            print(f'{GREEN}----------------------------------------{RESET}')
            
        else:
            return

    print(f'{MAGENTA}{BRIGHT}\n************************* Welcome *************************{RESET}')
    print(f'{CYAN}You are going to interact with your account in "Blofin.com"{RESET}')
    print(f'{CYAN}Pick One of The Options Below:{RESET}')
    print(f'{MAGENTA}{BRIGHT}***********************************************************\n{RESET}')
    

    try:
        prompt = input(f"{YELLOW}1. Place Order\n2. Pending Orders\n3. Open Positions\n4. Cancel Order\n5. Close Position\n6. Get Leverage\n7. Set Leverage\n8. Get Margin Mode\n9. Set Margin Mode\n10. Print API Credentials\n11. Modify API Credentials\n12. Get Balance\n13. Trade History\n14. Info About Size\n0. Exit\n\n> {RESET}")
    except:
        print(f"{RED}\nOperation cancelled by user{RESET}")
        return
    if prompt == '0':
        return
    if prompt == "1":
        try:
            valid_inputs = ['1', '2', '3', '4']
            price = None

            symbol = input(f'{YELLOW}Enter Symbol\nExample: [btc] | [eth]\n> {RESET}').upper().strip()
            b = Blofin(symbol+"-USDT")
            if not b.get_market_price()[1]:
                print(f"{RED}Invalid Symbol{RESET}")
                return
            order_type = input(f"{YELLOW}Order Type:\n1. limit\n2. market\n3. trigger\n4. post_only\n> {RESET}").lower().strip()
            if not order_type in valid_inputs:
                print(f'{RED}Invalid Input{RESET}')
                return
            position_side = input(f"{YELLOW}Position Side:\n1. long\n2. short\n> {RESET}").lower().strip()
            if not position_side in valid_inputs[:2]:
                print(f'{RED}Invalid Input{RESET}')
                return
            size = input(f'{YELLOW}Size (%): Example: [100] means "100%" of your balance\n> {RESET}').strip()
            try:
                size = float(size)
                if size < 1 or size > 100:
                    print(f'{RED}Size Must be 1-100{RESET}')
                    return
            except ValueError:
                print(f"{RED}Size is mandatory and must be digit{RESET}")
                return
            price = input(f"{YELLOW}Price:\n> {RESET}").lower().strip() if not order_type == '2' else print(f"{CYAN}Order Type: market{RESET}")
            try:
                if order_type != '2':
                    price = float(price)
                    if price <= 0:
                        print(f"{RED}Price Must be greater than 0{RESET}")
                        return
            except ValueError:
                print(f"{RED}Price is mandatory and must be digit{RESET}")
                return
            tp = input(f"{YELLOW}TP: (Optional)\n> {RESET}").strip()
            try:
                if tp:
                    tp = float(tp)
                    if tp <= 0:
                        print(f"{RED}TP Must be greater than 0{RESET}")
                        return
            except ValueError:
                print(f"{RED}TP must be digit{RESET}")
                return
            sl = input(f"{YELLOW}SL: (Optional)\n> {RESET}").strip()
            try:
                if sl:
                    sl = float(sl)
                    if sl <= 0:
                        print(f"{RED}SL Must be greater than 0{RESET}")
                        return
            except ValueError:
                print(f"{RED}SL must be digit{RESET}")
                return
        except:
            print(f"{RED}\nOperation cancelled by user{RESET}")
            return

        print(f'\n{CYAN}Please Wait...{RESET}')

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

        [size_in_contract, markPrice, final_size, lvg] = b.calculate_size(size, position_side, price)

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
            tp_in_usdt = round((final_size * cal_tp) / 100, 2)
        if cal_sl:
            sl_in_usdt = round((final_size * cal_sl) / 100 , 2)
            
        
        print(f'\n{LIGHTBLUE_EX}------------------------ Order Information -------------------{RESET}')
        print(f'{LIGHTBLUE_EX}Pair:               "{symbol}-USDT"{RESET}')
        print(f'{LIGHTBLUE_EX}Position Side:      "{position_side}"{RESET}')
        print(f'{LIGHTBLUE_EX}Order type:         "{order_type}"{RESET}')
        print(f'{LIGHTBLUE_EX}Leverage:           "{lvg}x"{RESET}')
        print(f'{LIGHTBLUE_EX}Size with Leverage: "{final_size} USDT"{RESET}')
        if order_type == "market":
            print(f'{LIGHTBLUE_EX}Price:              "{markPrice}"{RESET}')
        else:
            print(f'{LIGHTBLUE_EX}Price:              "{price}"{RESET}')
        if cal_tp:
            print(f'{LIGHTBLUE_EX}TP:                 "{tp}" => {GREEN}"{cal_tp}%" = "{tp_in_usdt} USDT"{RESET}')
        if cal_sl:
            print(f'{LIGHTBLUE_EX}SL:                 "{sl}" => {LIGHTRED_EX}"{cal_sl}%" = "{sl_in_usdt} USDT"{RESET}')
        print(f'{LIGHTBLUE_EX}--------------------------------------------------------------{RESET}')
        print(f'{YELLOW}* TP and SL calculation is approximate for market orders{Style.RESET_ALL}\n')

        try:
            sure = input(f"{Fore.YELLOW}\nDo you confirm? [y/n]\n> {Style.RESET_ALL}").lower().strip()
        except:
            print(f"{RED}\nOperation cancelled by user{RESET}")
            return
        if sure == "no" or sure == "n":
            print(f'{CYAN}Ok, See you later!{RESET}\n')
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
            id = input(f"{Fore.YELLOW}Enter Order/Algo ID (if you want to cancel more than one order, simpley put a comma between IDs ',')\nExample: '61404050, 1000060569014'\n> {Style.RESET_ALL}").strip()
            ids = id.split(',')
            for i in range(len(ids)):
                ids[i] = ids[i].strip()
                if not ids[i].isdigit():
                    print(f'{RED}Order Id is mandatory and must be digit{RESET}')
                    return
                
        except:
            print(f"{RED}\nOperation cancelled by user{RESET}")
            return

        b = Blofin()
        b.cancel_order(ids)

    elif prompt == "5":

        try:
            valid_inputs = ['1', '2']
            options = input(f"{YELLOW}\n1. Close One Position\n2. Close All Positions\n> {RESET}")
            if not options in valid_inputs:
                print(f'{RED}Invalid Input{RESET}')
                return
            
            if options == '1':
                symbol = input(f"{YELLOW}\nEnter Symbol: e.g \"btc\"\n> {RESET}").upper().strip()
                position_side = input(f"{Fore.YELLOW}Position Side:\n1. Long\n2. Short\n> {RESET}").strip()
                if not position_side in valid_inputs:
                    print(f'{RED}Invalid Input!{RESET}')
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
            print(f"{RED}\nOperation cancelled by user or something else went wrong!{RESET}")
            return
        
        
    
    elif prompt == "6":

        try:
            symbol = input(f"{YELLOW}\nEnter symbol(s):\nFor more than one, simply add ',' e,g. \"btc,eth\"\n> {RESET}").strip()
            symbols = symbol.split(',')
            for i in range(len(symbols)):
                symbols[i] = symbols[i].strip()
            modified_words = [element + '-usdt' for element in symbols]
            modified_symbols = ','.join(modified_words)
        except:
            print(f"{RED}\nOperation cancelled by user{RESET}")
            return
        b = Blofin()
        b.get_leverage(modified_symbols)

    elif prompt == "7":

        try:
            valid_inputs = ['1', '2', '3']
            symbol = input(f"{YELLOW}\nEnter Symbol: e.g \"btc\"\n> {RESET}").upper().strip()
            if not symbol:
                print(f'{RED}Symbol is mandatory{RESET}')
                return
            leverage = input(f"{YELLOW}Leverage:\n> {RESET}").strip()
            if not leverage or not leverage.isdigit():
                print(f'{RED}Leverage is mandatory and must be digit{RESET}')
                return
            position_side = input(f"{YELLOW}Position Side:\n1. Long\n2. Short\n3. Both\n> {RESET}").strip()
            if not position_side in valid_inputs:
                print(f'{Fore.RED}Invalid Input!{Style.RESET_ALL}')
                return
        except:
            print(f"{Fore.RED}\nOperation cancelled by user{Style.RESET_ALL}")
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
            marginMode = input(f"{Fore.YELLOW}\nMargin Mode:\n1. Isolated\n2. Cross\n> {Style.RESET_ALL}").strip()
            if not marginMode in valid_inputs:
                print(f'{Fore.RED}Invalid Input!{Style.RESET_ALL}')
                return
        except:
            print(f"{Fore.RED}\nOperation cancelled by user{Style.RESET_ALL}")
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
                print(f"{Fore.CYAN}{contents}{Style.RESET_ALL}")

    elif prompt == "11":

        try:
            modify = input(f'{Fore.YELLOW}\n1. Modify API Key\n2. Modify API Secret\n3. Modify Passphrase\n4. Modify All\n> {Style.RESET_ALL}').strip()
        except:
            print(f'{Fore.RED}\nOperation cancelled by user{Style.RESET_ALL}')
            return
        
        if modify == "1":

            try:
                api_key = input(f'{Fore.YELLOW}New API Key:\n> {Style.RESET_ALL}').strip()
            except:
                print(f'{Fore.RED}\nOperation cancelled by user{Style.RESET_ALL}')
                return
            
            if api_key:
                load_dotenv(envfile)
                set_key(envfile, 'API_KEY', api_key)
                print(f'{Fore.GREEN}API Key Updated!{Style.RESET_ALL}')
            else:
                print(f"{Fore.YELLOW}No input! No changes made!{Style.RESET_ALL}")

        elif modify == "2":

            try:
                api_secret = input(f'{Fore.YELLOW}New API Secret:\n> {Style.RESET_ALL}').strip()
            except:
                print(f'{Fore.RED}\nOperation cancelled by user{Style.RESET_ALL}')
                return

            if api_secret:
                load_dotenv(envfile)
                set_key(envfile, 'SECRET', api_secret)
                print(f'{Fore.GREEN}API Secret Updated{Style.RESET_ALL}')
            else:
                print(f'{Fore.YELLOW}No input! No changes made!{Style.RESET_ALL}')

        elif modify == "3":

            try:
                passphrase = input(f'{Fore.YELLOW}New Passphrase:\n> {Style.RESET_ALL}').strip()
            except:
                print(f'{Fore.RED}\nOperation cancelled by user{Style.RESET_ALL}')
                return
            
            if passphrase:
                load_dotenv(envfile)
                set_key(envfile, 'PASSPHRASE', passphrase)
                print(f'{Fore.GREEN}Passphrase Updated!{Style.RESET_ALL}')
            else:
                print(f'{Fore.YELLOW}No input! No changes made!{Style.RESET_ALL}')

        elif modify == "4":
                
            try:
                api_key = input(f'{Fore.YELLOW}New API Key:\n> {Style.RESET_ALL}').strip()
                api_secret = input(f'{Fore.YELLOW}New API Secret:\n> {Style.RESET_ALL}').strip()
                passphrase = input(f'{Fore.YELLOW}New Passphrase:\n> {Style.RESET_ALL}').strip()
            except:
                print(f'{Fore.RED}\nOperation cancelled by user{Style.RESET_ALL}')
                return

            if api_key and api_secret and passphrase:
                load_dotenv(envfile)
                set_key(envfile, 'API_KEY', api_key)
                set_key(envfile, 'SECRET', api_secret)
                set_key(envfile, 'PASSPHRASE', passphrase)
                print(f'{Fore.GREEN}API Key, Secret and Passphrase Updated!{Style.RESET_ALL}')
            else:
                print(f'{Fore.YELLOW}One or more fields are empty. No changes made!{Style.RESET_ALL}')
        
        else:
            print(f'{Fore.RED}Invalid Option!{Style.RESET_ALL}')
    
    elif prompt == "12":

        b = Blofin()
        b.check_balance()

    elif prompt == "13":
        try:
            symbol = input(f'{Fore.YELLOW}\nEnter symbol: [Default: All symbols]\n> {Style.RESET_ALL}')
            limit = input(f'{Fore.YELLOW}How many trades: [Default: 10]\n> {Style.RESET_ALL}')
            if not limit == '' and not limit.isdigit():
                print(f'{Fore.RED}Limit value must be digit{Style.RESET_ALL}')
                return
        except:
            print(f"{Fore.RED}\nOperation cancelled by user{Style.RESET_ALL}")
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
        print(f"{Fore.RED}\nInvalid input! Enter a number between 1-14\n{Style.RESET_ALL}")


run()
