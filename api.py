import requests
import json
import hmac
from hashlib import sha256
import base64
import time
import uuid
import os
import math
import datetime
from dotenv import load_dotenv
from colorama import Fore, Style, init

init()

class Blofin:
    def __init__(self, symbol=""):
        load_dotenv()
        self.symbol = symbol
        self.api_key = os.getenv("API_KEY")
        self.secret = os.getenv("SECRET")
        self.url = "https://openapi.blofin.com"
        # demo url: https://demo-trading-openapi.blofin.com
        self.passphrase = os.getenv("PASSPHRASE")

    ################################ GENERATE SIGNATURE ################################

    def __gen_signature(self, path, method, timestamp, nonce, body={}):
        if body:
            prehash_string = f"{path}{method}{timestamp}{nonce}{json.dumps(body)}"
        else:
            prehash_string = f"{path}{method}{timestamp}{nonce}"
        sign = base64.b64encode(hmac.new(self.secret.encode(), prehash_string.encode(), sha256).hexdigest().encode()).decode()
        headers = {
            "ACCESS-KEY":self.api_key,
            "ACCESS-SIGN":sign,
            "ACCESS-TIMESTAMP":str(timestamp),
            "ACCESS-NONCE":nonce,
            "ACCESS-PASSPHRASE":self.passphrase,
        }
        return headers

    ################################# SET LEVERAGE #####################################

    def set_leverage(self, leverage, positionSide):
        def ok(pside):
            print(f'{Fore.GREEN}\n#####################################{Style.RESET_ALL}')
            print(f'{Fore.GREEN}Set Leverage Successfully{Style.RESET_ALL}')
            print(f'{Fore.GREEN}Symbol:        {self.symbol}{Style.RESET_ALL}')
            print(f'{Fore.GREEN}Leverage       {leverage}x{Style.RESET_ALL}') 
            print(f'{Fore.GREEN}Position Side: {pside}\n{Style.RESET_ALL}')
            print(f'{Fore.GREEN}#####################################\n{Style.RESET_ALL}')

        def error(data):
            print(f'{Fore.RED}\nError Code: {data['code']}{Style.RESET_ALL}')
            print(f'{Fore.RED}Error Message: {data['msg']}{Style.RESET_ALL}')
            print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
            print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')

        def send_request(pside):
            method = "POST"
            path = "/api/v1/account/set-leverage"
            nonce = str(uuid.uuid4())
            timestamp = int(round(time.time() * 1000))
            body = {
                "instId":self.symbol,
                "leverage":leverage,
                "marginMode":self.get_margin_mode(True),
                "positionSide":pside
            }
            h = self.__gen_signature(path, method, timestamp, nonce, body)
            response = requests.request(method, self.url+path, headers=h, json=body)
            data = response.json()
            if data['code'] == '0':
                ok(pside)
            else:
                error(data)
        
        try:
            if positionSide == 'both':
                for pside in ['long', 'short']:
                    send_request(pside)
            else:
                send_request(positionSide)
        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}Http error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')
    
    ########################################## GET LEVERAGE ####################################

    def get_leverage(self, symbols):
        path = f"/api/v1/account/batch-leverage-info?instId={symbols}&marginMode={self.get_margin_mode(True)}"
        method = "GET"
        nonce = str(uuid.uuid4())
        timestamp = int(round(time.time() * 1000))

        try:
            h = self.__gen_signature(path, method, timestamp, nonce)
            res = requests.request(method, self.url+path, headers=h)
            data = res.json()
            if data['code'] == "0":
                info = data['data']
                i = 0
                while( i<len(info) -1 ):
                    print(f'{Fore.CYAN}\n#####################{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}Symbol: {info[i]['instId']}{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}Long;  Leverage: {info[i]['leverage']}x{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}Short; Leverage: {info[i+1]['leverage']}x{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}#####################\n{Style.RESET_ALL}')

                    i+=2

            else:
                print(f'{Fore.RED}\nError Code:    {data['code']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Error Message: "{data['msg']}"{Style.RESET_ALL}')
                print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')

        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')

    ################################# PLACE TRIGGER ORDER ######################################

    def place_trigger_order(self, positionSide, side, size, tp, sl, price):
        method = "POST"
        path = "/api/v1/trade/order-algo"
        nonce = str(uuid.uuid4())
        timestamp = int(round(time.time() * 1000))
        body = {
            "instId":self.symbol,
            "marginMode":self.get_margin_mode(True),
            "positionSide":positionSide,
            "side":side,
            "size":str(size),
            "orderPrice":"-1",
            "orderType":"trigger",
            "triggerPrice":str(price),
            "triggerPriceType": "last",
            "attachAlgoOrders":[{
                "tpTriggerPrice":str(tp),
                "tpOrderPrice":str(tp),
                "tpTriggerPriceType":"last",
                "slTriggerPrice":str(sl),
                "slOrderPrice":str(sl),
                "slTriggerPriceType":"last"
            }]
        }

        try:
            h = self.__gen_signature(path, method, timestamp, nonce, body)
            response = requests.request(method, self.url+path, headers=h, json=body)
            data = response.json()
            if data['code'] == "0":
                if data['data']['code'] == "0":
                    id = data['data']['algoId']
                    print(f'{Fore.GREEN}Success{Style.RESET_ALL}')
                    if positionSide == "long":
                        print(f'{Fore.GREEN}\nTrigger Order Placed: Long{Style.RESET_ALL}')
                        print(f"{Fore.GREEN}Order ID: {id}{Style.RESET_ALL}")
                    else:
                        print(f'{Fore.GREEN}\nTrigger Order Placed: Short{Style.RESET_ALL}')
                        print(f"{Fore.GREEN}Order ID: {id}\n{Style.RESET_ALL}")
                else:
                    print(f'{Fore.RED}\nError Code: {data['data']['code']}{Style.RESET_ALL}')
                    print(f'{Fore.RED}Error Message: "{data['data']['msg']}"\n{Style.RESET_ALL}')
            else:
                print(f"{Fore.RED}\nError Code: {data['code']}{Style.RESET_ALL}")
                print(f'{Fore.RED}Error Message: {data['msg']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')

        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')

    ########################### PLACE LIMIT ORDER/TAKE MARKET POSITION #########################

    def place_normal_order(self, positionSide, side, orderType, size, tp, sl, price=""):
        method = "POST"
        path = "/api/v1/trade/order"
        nonce = str(uuid.uuid4())
        timestamp = int(round(time.time() * 1000))
        body = {
            "instId":self.symbol,
            "marginMode":self.get_margin_mode(True),
            "positionSide":positionSide,
            "side":side,
            "orderType":orderType,
            "price":str(price),
            "size":str(size),
            "tpTriggerPrice": str(tp),
            "tpOrderPrice": str(tp),
            "slTriggerPrice":str(sl),
            "slOrderPrice": str(sl)
        }

        if orderType == "market":
            body.pop('price')

        try:
            
            h = self.__gen_signature(path, method, timestamp, nonce, body)
            response = requests.request(method, self.url+path, headers=h, json=body)
            data = response.json()
            if not orderType == "market":
                if data['code'] == "0":
                    if data['data'][0]['code'] == "0":
                        print(f"{Fore.GREEN}Success{Style.RESET_ALL}")
                        if positionSide == "long":
                            print(f'{Fore.GREEN}\nLong Order Placed{Style.RESET_ALL}')
                            print(f"{Fore.GREEN}Order ID: {data['data'][0]['orderId']}{Style.RESET_ALL}")
                        else:
                            print(f'{Fore.GREEN}\nShort Order Placed{Style.RESET_ALL}')
                            print(f"{Fore.GREEN}Order ID: {data['data'][0]['orderId']}\n{Style.RESET_ALL}")
                else:
                    if data['code'] == "1":
                        print(f'{Fore.RED}\nError Code: {data['data'][0]['code']}{Style.RESET_ALL}')
                        print(f'{Fore.RED}Error Message: {data['msg']}. {data['data'][0]['msg']}\n{Style.RESET_ALL}')
                        
                        
                    else:
                        print(f'{Fore.RED}\nError Code: {data['code']}{Style.RESET_ALL}')
                        print(f'{Fore.RED}Error Message: {data['msg']}\n{Style.RESET_ALL}')
            else:
                if data['code'] == "0":
                    if data['data'][0]['code'] == "0":
                        if positionSide == "long":
                            print(f'{Fore.GREEN}\nLong Position Succussfully Taken\n{Style.RESET_ALL}')
                        else:
                            print(f'{Fore.GREEN}\nShort Position Succussfully Taken\n{Style.RESET_ALL}')
                else:
                    if data['code'] == "1":
                        print(f'{Fore.RED}Error Code: {data['data'][0]['code']}{Style.RESET_ALL}')
                        print(f'{Fore.RED}Error Message: {data['msg']}. {data['data']['msg']}{Style.RESET_ALL}')
                    else:
                        print(f'{Fore.RED}\nError Code: {data['code']}{Style.RESET_ALL}')
                        print(f'{Fore.RED}Error Message: {data['msg']}{Style.RESET_ALL}')
                        print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                        print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')

        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')

    ####################################### CANCEL ORDER #######################################

    def cancel_order(self, ids):
        for id in ids:
            if len(id) >= 13:
                path = "/api/v1/trade/cancel-order"
                body = { "orderId": id }
            else:
                path = "/api/v1/trade/cancel-algo"
                body = { "algoId": id }
            
            method = "POST"
            timestamp = int(round(time.time() * 1000))
            nonce = str(uuid.uuid4())

            try:
                h = self.__gen_signature(path, method, timestamp, nonce, body)
                response = requests.request(method, self.url+path, headers=h, json=body)
                data = response.json()
                
                if data['code'] == "0":
                    # trigger/algo
                    if len(id) < 13:
                        if data['data']['code'] == "0":
                            print(f"{Fore.GREEN}Trigger Order with ID {id} has been Canceled{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}Error Code: {data['data']['code']}{Style.RESET_ALL}")
                            print(f'{Fore.RED}Error Message: "{data['data']['msg']}"{Style.RESET_ALL}')
                    # normal
                    else:
                        if data['data'][0]['code'] == "0":
                            print(f"{Fore.GREEN}Order with ID {id} has been Canceled{Style.RESET_ALL}")
                        else:
                            print(f'{Fore.RED}Error:{Style.RESET_ALL}')
                            print(f'{Fore.RED}{data}{Style.RESET_ALL}')
                else:
                    print(f'{Fore.RED}\nError Code: {data['code']}{Style.RESET_ALL}')
                    print(f'{Fore.RED}Error Message: "{data['msg']}"{Style.RESET_ALL}')
                    print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                    print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')
                
            except requests.exceptions.HTTPError as http_err:
                print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
            except Exception as err:
                print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')

    ##################################### CLOSE POSITIONS ######################################

    def close_position(self, position_side='', isAll=False):

        def _close_single_position(inst_id, pos_side):
            path = "/api/v1/trade/close-position"
            method = "POST"
            timestamp = int(round(time.time() * 1000))
            nonce = str(uuid.uuid4())
            body = {
                "instId": inst_id,
                "marginMode": self.get_margin_mode(True),
                "positionSide": pos_side
            }
            try:
                h = self.__gen_signature(path, method, timestamp, nonce, body)
                response = requests.request(method, self.url + path, headers=h, json=body)
                data = response.json()
                if data['code'] == "0":
                    print(f"{Fore.GREEN}\n{inst_id}; {pos_side.capitalize()} Position Closed\n{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}\nError Code: {data['code']}{Style.RESET_ALL}")
                    print(f'{Fore.RED}Error Message: "{data["msg"]}"{Style.RESET_ALL}')
                    print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                    print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')
            except requests.exceptions.HTTPError as http_err:
                print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
            except Exception as err:
                print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')

        

        open_positions = self.get_open_positions(True)
        if not open_positions:
            print(f'{Fore.YELLOW}There Are No Open Positions!{Style.RESET_ALL}')
            return

        if isAll:
            for item in open_positions:
                _close_single_position(item['instId'], item['positionSide'])
        else:
            _close_single_position(self.symbol, position_side)

    ################################ GET OPEN TRIGGER ORDERS ###################################

    def get_open_trigger_orders(self):
        method = "GET"
        path = "/api/v1/trade/orders-algo-pending?orderType=trigger"
        nonce = str(uuid.uuid4())
        timestamp = int(round(time.time() * 1000))
        try:
            h = self.__gen_signature(path, method, timestamp, nonce)
            res = requests.request(method, self.url+path, headers = h)
            data = res.json()
            if data['code'] == "0":
                info = data['data']
                if info:
                    print(f'{Fore.CYAN}{len(info)} Pending Trigger Order(s){Style.RESET_ALL}')
                    for item in info:
                        print(f'{Fore.CYAN}\n###############################################{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Symbol:        {item['instId']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Algo ID:       {item['algoId']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Size:          {item['size']} Contract(s){Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Leverage:      {item['leverage']}x{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Position Side: {item['positionSide']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Trigger Price: {item['triggerPrice']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}TP:            {item['attachAlgoOrders'][0]['tpTriggerPrice']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}SL:            {item['attachAlgoOrders'][0]['slTriggerPrice']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Margin Mode:   {item['marginMode']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Time:          {datetime.datetime.fromtimestamp(int(item['createTime']) / 1000)}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}###############################################\n{Style.RESET_ALL}')
                else:
                    print(f'{Fore.YELLOW}0 Pending Trigger Orders{Style.RESET_ALL}')
            else:
                print(f'{Fore.RED}\nError Code:    {data['code']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Error Message: {data['msg']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')

        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')

    ################################# GET OPEN NORMAL ORDERS ###################################

    def get_open_normal_orders(self):
        path = "/api/v1/trade/orders-pending"
        method = "GET"
        nonce = str(uuid.uuid4())
        timestamp = int(round(time.time() * 1000))

        try:
            h = self.__gen_signature(path, method, timestamp, nonce)
            res = requests.request(method, self.url+path, headers = h)
            data = res.json()
            if data['code'] == "0":
                info = data['data']
                if info:
                    print(f'{Fore.CYAN}{len(info)} Pending Normal Order(s){Style.RESET_ALL}')
                    for item in info:
                        print(f'{Fore.CYAN}\n###############################################{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Symbol:        {item['instId']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Order ID:      {item['orderId']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Size:          {item['size']} Contract(s){Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Leverage:      {item['leverage']}x{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Position Side: {item['positionSide']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Order Type:    {item['orderType']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Price:         {item['price']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}TP:            {item['tpTriggerPrice']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}SL:            {item['slTriggerPrice']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Filled Size:   {item['filledSize']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Margin Mode:   {item['marginMode']}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}Time:          {datetime.datetime.fromtimestamp(int(item['createTime']) / 1000)}{Style.RESET_ALL}')
                        print(f'{Fore.CYAN}###############################################\n{Style.RESET_ALL}')
                else:
                    print(f'{Fore.YELLOW}0 Pending Normal Orders{Style.RESET_ALL}')
            else:
                print(f'{Fore.RED}\nError Code:    {data['code']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Error Message: {data['msg']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')

        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')

    ##################################### GET MARKET PRICE #####################################

    def get_market_price(self):
        method = "GET"
        path = f"/api/v1/market/mark-price?instId={self.symbol}"

        try:
            res = requests.request(method, self.url+path)
            data = res.json()
            if data['code'] == "0":
                return [float(data['data'][0]['markPrice']) , True]
            else:
                return [0 , False]

        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')
    
    #################################### GET OPEN POSITIONS ####################################

    def get_open_positions(self, fromInside=False):
        method = "GET"
        path = "/api/v1/account/positions"
        nonce = str(uuid.uuid4())
        timestamp = int(round(time.time() * 1000))
        try:
            h = self.__gen_signature(path, method, timestamp, nonce)
            res = requests.request(method, self.url+path, headers = h)
            data = res.json()
            if data['code'] == "0":
                info = data['data']
                if info:
                    list_to_return = []
                    print(f'{Fore.CYAN}{len(info)} Open Position(s){Style.RESET_ALL}')
                    for item in info:
                        if fromInside:
                            list_to_return.append({'instId': item['instId'], 'positionSide': item['positionSide']})
                        else:
                            print(f'{Fore.CYAN}\n#####################################{Style.RESET_ALL}')
                            print(f'{Fore.CYAN}Symbol:         {item['instId']}{Style.RESET_ALL}')
                            print(f'{Fore.CYAN}Position Id:    {item['positionId']}{Style.RESET_ALL}')
                            print(f'{Fore.CYAN}Margin Mode:    {item['marginMode']}{Style.RESET_ALL}')
                            print(f'{Fore.CYAN}Position Side:  {item['positionSide']}{Style.RESET_ALL}')
                            print(f'{Fore.CYAN}Size:           {item['positions']} Contract(s){Style.RESET_ALL}')
                            print(f'{Fore.CYAN}Leverage        {item['leverage']}x{Style.RESET_ALL}')
                            print(f'{Fore.CYAN}Price:          {item['averagePrice']}{Style.RESET_ALL}')
                            print(f'{Fore.CYAN}Market Price:   {item['markPrice']}{Style.RESET_ALL}')
                            print(f'{Fore.CYAN}Margin:         {item['margin']}{Style.RESET_ALL}')
                            print(f'{Fore.CYAN}Liq Price:      {item['liquidationPrice']}{Style.RESET_ALL}')
                            print(f'{Fore.CYAN}Unrealized PNL: {item['unrealizedPnl']}{Style.RESET_ALL}')
                            print(f'{Fore.CYAN}Time:           {datetime.datetime.fromtimestamp(int(item['createTime']) / 1000)}{Style.RESET_ALL}')
                            print(f'{Fore.CYAN}#####################################\n{Style.RESET_ALL}')
                    
                    return list_to_return
                else:
                    print(f'{Fore.YELLOW}0 Open Positions{Style.RESET_ALL}')
                    return []

            else:
                print(f'{Fore.RED}\nError Code: {data['code']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Error Message: {data['msg']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')

        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')
    
    ###################################### CHECK BALANCE #######################################

    def check_balance(self):
        path = "/api/v1/account/balance"
        method = "GET"
        timestamp = int(round(time.time() * 1000))
        nonce = str(uuid.uuid4())
        
        try:
            h = self.__gen_signature(path, method, timestamp, nonce)
            response = requests.request(method, self.url+path, headers=h)
            data = response.json()
            if data['code'] == "0":
                info = data['data']['details'][0]
                print(f'{Fore.CYAN}\n############### Balance ###############{Style.RESET_ALL}')
                print(f'{Fore.CYAN}Currency:        {info['currency']}{Style.RESET_ALL}')
                print(f'{Fore.CYAN}Total Equity:    {round(float(info['equity']), 2)}{Style.RESET_ALL}')
                print(f'{Fore.CYAN}Available:       {round(float(info['available']), 2)}{Style.RESET_ALL}')
                print(f'{Fore.CYAN}Isolated Equity: {round(float(info['isolatedEquity']), 2)}{Style.RESET_ALL}')
                print(f'{Fore.CYAN}Order Frozen:    {round(float(info['orderFrozen']), 2)}{Style.RESET_ALL}')
                print(f'{Fore.CYAN}#######################################\n{Style.RESET_ALL}')
                return round(float(info['available']), 2)
            else:
                print(f'{Fore.RED}\nError Code: {data['code']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Error Message: {data['msg']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')
            
        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')

    ###################################### SET MARGIN MODE #####################################

    def set_margin_mode(self, marginMode):
        path = "/api/v1/account/set-margin-mode"
        method = "POST"
        timestamp = int(round(time.time() * 1000))
        nonce = str(uuid.uuid4())

        body = {"marginMode": marginMode}

        try:
            h = self.__gen_signature(path, method, timestamp, nonce, body)
            response = requests.request(method, self.url+path, headers=h, json=body)
            data = response.json()
            if data['code'] == "0":
                print(f'{Fore.GREEN}\nMargin Mode Set: {data['data']['marginMode']}\n{Style.RESET_ALL}')
            else:
                print(f'{Fore.RED}\nError Code: {data['code']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Error Message: {data['msg']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')
            
        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')

    ###################################### GET MARGIN MODE #####################################

    def get_margin_mode(self, from_inside=False):
        path = "/api/v1/account/margin-mode"
        method = "GET"
        timestamp = int(round(time.time() * 1000))
        nonce = str(uuid.uuid4())

        try:
            h = self.__gen_signature(path, method, timestamp, nonce)
            response = requests.request(method, self.url+path, headers=h)
            data = response.json()
            if data['code'] == "0":
                if not from_inside:
                    print(f'{Fore.CYAN}\nMargin Mode: {data['data']['marginMode']}\n{Style.RESET_ALL}')
                else:
                    return data['data']['marginMode']
            else:
                print(f'{Fore.RED}\nError Code: {data['code']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Error Message: {data['msg']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')
            
        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')


    ##################################### GET TRADE HISTORY ####################################

    def get_trade_history(self, limit="10", symbol=""):
        if symbol:
            path = f'/api/v1/trade/fills-history?instId={symbol}-usdt&limit={limit}'
        else:
            path = f'/api/v1/trade/fills-history?limit={limit}'

        method = "GET"
        timestamp = int(round(time.time() * 1000))
        nonce = str(uuid.uuid4())

        try:
            h = self.__gen_signature(path, method, timestamp, nonce)
            response = requests.request(method, self.url+path, headers=h)
            data = response.json()

            if data['code'] == "0":
                print(f'{Fore.CYAN}\nTrade History:{Style.RESET_ALL}')
                for item in data['data']:
                    print(f'{Fore.CYAN}\n##########################################{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}Symbol:        {item['instId']}{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}Order ID:      {item['orderId']}{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}Trade ID:      {item['tradeId']}{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}Side:          {item['side']}{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}Position Side: {item['positionSide']}{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}Price:         {item['fillPrice']}{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}Size:          {item['fillSize']}{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}Fee:           {item['fee']}{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}Time:          {datetime.datetime.fromtimestamp(int(item['ts']) / 1000)}{Style.RESET_ALL}')
                    print(f'{Fore.CYAN}##########################################\n{Style.RESET_ALL}')
            else:
                print(f'{Fore.RED}\nError Code: {data['code']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Error Message: {data['msg']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')

        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')
    
    #################################### GET CONTRACT INFO #####################################

    def contract_info(self):
        path = f'/api/v1/market/instruments?instId={self.symbol}'
        method ='GET'

        try:
            res = requests.request(method, self.url+path)
            data = res.json()
            if data['code'] == "0":
                contract_value = float(data['data'][0]['contractValue'])
                min_size = float(data['data'][0]['minSize'])
                return [contract_value, min_size]
            else:
                print(f"{Fore.RED}Error in receiving contract info{Style.RESET_ALL}")

        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')

    ##################################### GET_LEVERAGE ########################################

    def leverage(self, position_side):
        path = f'/api/v1/account/batch-leverage-info?instId={self.symbol}&marginMode={self.get_margin_mode(True)}'
        method = 'GET'
        timestamp = int(round(time.time() * 1000))
        nonce = str(uuid.uuid4())

        try:
            h = self.__gen_signature(path, method, timestamp, nonce)
            response = requests.request(method, self.url+path, headers=h)
            data = response.json()
            if data['code'] == "0":
                if position_side == 'long':
                    return int(data['data'][0]['leverage'])
                elif position_side == 'short':
                    return int(data['data'][1]['leverage'])
            else:
                print(f'{Fore.RED}\nError Code: {data['code']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Error Message: {data['msg']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Please refer to the docs:{Style.RESET_ALL}')
                print(f'{Fore.RED}https://docs.blofin.com/index.html#errors\n{Style.RESET_ALL}')

        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')

    ##################################### Calculate Size #######################################

    def calculate_size(self, size, position_side, price=None):
        """
        Calculate contract size based on balance, leverage, and contract info.
        Returns [size_in_contract, price, final_size_usdt, leverage_multiplier].
        """
        balance = self.check_balance()
        contract_value, min_size = self.contract_info()
        size_in_usdt = round((balance * size) / 100, 2)
        leverage_multiplier = self.leverage(position_side)
        size_with_leverage = size_in_usdt * leverage_multiplier

        if price is None:
            price = self.get_market_price()[0]

        each_contract_in_usdt = contract_value * price

        print(f"{Fore.CYAN}{size}% of Balance: {size_in_usdt} USDT{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Leverage: {leverage_multiplier}x{Style.RESET_ALL}")

        precision = abs(int(round(math.log10(min_size)))) if min_size < 1 else 0
        multiplier = 10 ** precision if precision else 1

        size_in_contract = math.floor((size_with_leverage / each_contract_in_usdt) * multiplier) / multiplier
        final_size_usdt = size_in_contract * each_contract_in_usdt

        print(f"{Fore.CYAN}{size_in_contract} Contract(s) (With leverage){Style.RESET_ALL}")
        return [size_in_contract, price, final_size_usdt, leverage_multiplier]
        
    ##################################### API AUTHENTICATION #####################################

    def API_auth(self, api_key, secret, passphrase):
        path = '/api/v1/account/margin-mode'
        method = 'GET'
        timestamp = int(round(time.time() * 1000))
        nonce = str(uuid.uuid4())
        prehash_string = f"{path}{method}{timestamp}{nonce}"
        sign = base64.b64encode(hmac.new(secret.encode(), prehash_string.encode(), sha256).hexdigest().encode()).decode()
        headers = {
            "ACCESS-KEY":api_key,
            "ACCESS-SIGN":sign,
            "ACCESS-TIMESTAMP":str(timestamp),
            "ACCESS-NONCE":nonce,
            "ACCESS-PASSPHRASE":passphrase
        }

        try:
            response = requests.request(method, self.url+path, headers=headers)
            data = response.json()
            
            if data['code'] == '0':
                return True
            else:
                print(f'{Fore.RED}\n- Error Code: {data['code']}{Style.RESET_ALL}')
                print(f'{Fore.RED}- Message: {data['msg']}{Style.RESET_ALL}')
                print(f'{Fore.RED}Try again\n{Style.RESET_ALL}')
                return False
        except requests.exceptions.HTTPError as http_err:
            print(f'{Fore.RED}HTTP error occurred: {http_err}{Style.RESET_ALL}')
        except Exception as err:
            print(f'{Fore.RED}Other error occurred: {err}{Style.RESET_ALL}')
        
    ########################################## Info ##############################################

    def print_info(self):
        print(f'{Fore.YELLOW}{Style.BRIGHT}********************************************* IMPORTANT ***************************************************{Style.RESET_ALL}')
        print(f"{Fore.YELLOW}If the actual order size shows less than entered, don't worry!\nSize calculation in Blofin API is a little tricky!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}For example: minimum size for bitcoin is 0.1 contract. 0.15 is not acceptable! Must be either 0.1 or 0.2\nIn this case the script floors 0.15 to 0.1{Style.RESET_ALL}")
        print(f'{Fore.YELLOW}{Style.BRIGHT}***********************************************************************************************************\n{Style.RESET_ALL}')

