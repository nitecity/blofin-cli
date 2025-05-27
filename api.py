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
            print('\n#####################################')
            print('Set Leverage Successfully')
            print(f'Symbol:        {self.symbol}')
            print(f'Leverage       {leverage}x') 
            print(f'Position Side: {pside}\n')
            print('#####################################\n')

        def error(data):
            print(f'\nError Code: {data['code']}')
            print(f'Error Message: {data['msg']}')
            print('Please refer to the docs:')
            print('https://docs.blofin.com/index.html#errors\n')

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
            print(f'Http error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
    
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
                    print('\n#####################')
                    print(f'Symbol: {info[i]['instId']}')
                    print(f'Long;  Leverage: {info[i]['leverage']}x')
                    print(f'Short; Leverage: {info[i+1]['leverage']}x')
                    print('#####################\n')

                    i+=2

            else:
                print(f'\nError Code:    {data['code']}')
                print(f'Error Message: "{data['msg']}"')
                print('Please refer to the docs:')
                print('https://docs.blofin.com/index.html#errors\n')

        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

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
                    if positionSide == "long":
                        print('\nLong:')
                        print(f"Order ID: {id}")
                        print('Order ID saved in "order_ids.txt"\n')
                        with open('order_ids.txt', 'a') as file:
                            file.write(f"{id}\n")
                    else:
                        print('\nShort:')
                        print(f"Order ID: {id}\n")
                        with open('order_ids.txt', 'a') as file:
                            file.write(f"{id}\n")
                else:
                    print(f'\nError Code: {data['data']['code']}')
                    print(f'Error Message: "{data['data']['msg']}"\n')
            else:
                print(f"\nError Code: {data['code']}")
                print(f'Error Message: {data['msg']}')
                print('Please refer to the docs:')
                print('https://docs.blofin.com/index.html#errors\n')

        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

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
                        print("Success")
                        if positionSide == "long":
                            print('\nLong Order Placed')
                            print(f"Order ID: {data['data'][0]['orderId']}")
                            print("Order ID saved in \"order_ids.txt\"\n")
                            with open('order_ids.txt', 'a') as file:
                                file.write(f"{data['data'][0]['orderId']}\n")
                        else:
                            print('\nShort Order Placed')
                            print(f"Order ID: {data['data'][0]['orderId']}\n")
                            with open('order_ids.txt', 'a') as file:
                                file.write(f"{data['data'][0]['orderId']}\n")
                else:
                    if data['code'] == "1":
                        print(f'\nError Code: {data['data'][0]['code']}')
                        print(f'Error Message: {data['msg']}. {data['data'][0]['msg']}\n')
                        
                        
                    else:
                        print(f'\nError Code: {data['code']}')
                        print(f'Error Message: {data['msg']}\n')
            else:
                if data['code'] == "0":
                    if data['data'][0]['code'] == "0":
                        if positionSide == "long":
                            print('\nLong Position Succussfully Taken\n')
                        else:
                            print('\nShort Position Succussfully Taken\n')
                else:
                    if data['code'] == "1":
                        print(f'Error Code: {data['data'][0]['code']}')
                        print(f'Error Message: {data['msg']}. {data['data']['msg']}')
                    else:
                        print(f'\nError Code: {data['code']}')
                        print(f'Error Message: {data['msg']}')
                        print('Please refer to the docs:')
                        print('https://docs.blofin.com/index.html#errors\n')

        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

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
                            print(f"Trigger Order with ID {id} has been Canceled")
                            with open('order_ids.txt', 'r') as file:
                                lines = file.readlines()
                            with open('order_ids.txt', 'w') as file:
                                for line in lines:
                                    if line != id+"\n":
                                        file.write(line)
                        else:
                            print(f"Error Code: {data['data']['code']}")
                            print(f'Error Message: "{data['data']['msg']}"')
                    # normal
                    else:
                        if data['data'][0]['code'] == "0":
                            print(f"Order with ID {id} has been Canceled")
                            with open('order_ids.txt', 'r') as file:
                                lines = file.readlines()
                            with open('order_ids.txt', 'w') as file:
                                for line in lines:
                                    if line != id+"\n":
                                        file.write(line)
                        else:
                            print('Error:')
                            print(data)
                else:
                    print(f'\nError Code: {data['code']}')
                    print(f'Error Message: "{data['msg']}"')
                    print('Please refer to the docs:')
                    print('https://docs.blofin.com/index.html#errors\n')
                
            except requests.exceptions.HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}')

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
                    print(f"\n{inst_id}; {pos_side.capitalize()} Position Closed\n")
                else:
                    print(f"\nError Code: {data['code']}")
                    print(f'Error Message: "{data["msg"]}"')
                    print('Please refer to the docs:')
                    print('https://docs.blofin.com/index.html#errors\n')
            except requests.exceptions.HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}')

        

        open_positions = self.get_open_positions(True)
        if not open_positions:
            print('There Are No Open Positions!')
            return

        if isAll:
            for item in open_positions:
                _close_single_position(item['intId'], item['positionSide'])
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
                    print(f'{len(info)} Pending Trigger Order(s)')
                    for item in info:
                        print(f'\n#####################################')
                        print(f'Symbol:        {item['instId']}')
                        print(f'Algo ID:       {item['algoId']}')
                        print(f'Size:          {item['size']} Contract(s)')
                        print(f'Leverage:      {item['leverage']}x')
                        print(f'Position Side: {item['positionSide']}')
                        print(f'Trigger Price: {item['triggerPrice']}')
                        print(f'TP:            {item['attachAlgoOrders'][0]['tpTriggerPrice']}')
                        print(f'SL:            {item['attachAlgoOrders'][0]['slTriggerPrice']}')
                        print(f'Margin Mode:   {item['marginMode']}')
                        print(f'Time:          {datetime.datetime.fromtimestamp(int(item['createTime']) / 1000)}')
                        print(f'#####################################\n')
                else:
                    print('0 Pending Trigger Orders')
            else:
                print(f'\nError Code:    {data['code']}')
                print(f'Error Message: {data['msg']}')
                print('Please refer to the docs:')
                print('https://docs.blofin.com/index.html#errors\n')

        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

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
                    print(f'{len(info)} Pending Normal Order(s)')
                    for item in info:
                        print(f'\n#####################################')
                        print(f'Symbol:        {item['instId']}')
                        print(f'Order ID:      {item['orderId']}')
                        print(f'Size:          {item['size']} Contract(s)')
                        print(f'Leverage:      {item['leverage']}x')
                        print(f'Position Side: {item['positionSide']}')
                        print(f'Order Type:    {item['orderType']}')
                        print(f'Price:         {item['price']}')
                        print(f'TP:            {item['tpTriggerPrice']}')
                        print(f'SL:            {item['slTriggerPrice']}')
                        print(f'Filled Size:   {item['filledSize']}')
                        print(f'Margin Mode:   {item['marginMode']}')
                        print(f'Time:          {datetime.datetime.fromtimestamp(int(item['createTime']) / 1000)}')
                        print(f'#####################################\n')
                else:
                    print('0 Pending Normal Orders')
            else:
                print(f'\nError Code:    {data['code']}')
                print(f'Error Message: {data['msg']}')
                print('Please refer to the docs:')
                print('https://docs.blofin.com/index.html#errors\n')

        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

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
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
    
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
                    print(f'{len(info)} Open Position(s)')
                    for item in info:
                        if fromInside:
                            list_to_return.append({'intId': item['instId'], 'positionSide': item['positionSide']})
                        else:
                            print(f'\n#####################################')
                            print(f'Symbol:         {item['instId']}')
                            print(f'Position Id:    {item['positionId']}')
                            print(f'Margin Mode:    {item['marginMode']}')
                            print(f'Position Side:  {item['positionSide']}')
                            print(f'Size:           {item['positions']} Contract(s)')
                            print(f'Leverage        {item['leverage']}x')
                            print(f'Price:          {item['averagePrice']}')
                            print(f'Market Price:   {item['markPrice']}')
                            print(f'Margin:         {item['margin']}')
                            print(f'Liq Price:      {item['liquidationPrice']}')
                            print(f'Unrealized PNL: {item['unrealizedPnl']}')
                            print(f'Time:           {datetime.datetime.fromtimestamp(int(item['createTime']) / 1000)}')
                            print(f'#####################################\n')
                    
                    return list_to_return
                else:
                    print('0 Open Positions')
                    return []

            else:
                print(f'\nError Code: {data['code']}')
                print(f'Error Message: {data['msg']}')
                print('Please refer to the docs:')
                print('https://docs.blofin.com/index.html#errors\n')

        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
    
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
                print('\n################## Balance ##################')
                print(f'Currency:        {info['currency']}')
                print(f'Total Equity:    {round(float(info['equity']), 2)}')
                print(f'Available:       {round(float(info['available']), 2)}')
                print(f'Isolated Equity: {round(float(info['isolatedEquity']), 2)}')
                print('#############################################\n')
                return round(float(info['available']), 2)
            else:
                print(f'\nError Code: {data['code']}')
                print(f'Error Message: {data['msg']}')
                print('Please refer to the docs:')
                print('https://docs.blofin.com/index.html#errors\n')
            
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

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
                print(f'\nMargin Mode Set: {data['data']['marginMode']}\n')
            else:
                print(f'\nError Code: {data['code']}')
                print(f'Error Message: {data['msg']}')
                print('Please refer to the docs:')
                print('https://docs.blofin.com/index.html#errors\n')
            
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

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
                    print(f'\nMargin Mode: {data['data']['marginMode']}\n')
                else:
                    return data['data']['marginMode']
            else:
                print(f'\nError Code: {data['code']}')
                print(f'Error Message: {data['msg']}')
                print('Please refer to the docs:')
                print('https://docs.blofin.com/index.html#errors\n')
            
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')


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
                print('\nTrade History:')
                for item in data['data']:
                    print(f'\n#####################################')
                    print(f'Symbol:        {item['instId']}')
                    print(f'Order ID:      {item['orderId']}')
                    print(f'Trade ID:      {item['tradeId']}')
                    print(f'Side:          {item['side']}')
                    print(f'Position Side: {item['positionSide']}')
                    print(f'Price:         {item['fillPrice']}')
                    print(f'Size:          {item['fillSize']}')
                    print(f'Fee:           {item['fee']}')
                    print(f'Time:          {datetime.datetime.fromtimestamp(int(item['ts']) / 1000)}')
                    print(f'#####################################\n')
            else:
                print(f'\nError Code: {data['code']}')
                print(f'Error Message: {data['msg']}')
                print('Please refer to the docs:')
                print('https://docs.blofin.com/index.html#errors\n')

        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
    
    #################################### GET CONTRACT INFO #####################################

    def contract_info(self):
        path = f'/api/v1/market/instruments?instId={self.symbol}'
        method ='GET'

        try:
            res = requests.request(method, self.url+path)
            data = res.json()
            if data['code'] == "0":
                contract_value = float(data['data'][0]['contractValue'])
                min_size = data['data'][0]['minSize']
                return [contract_value, min_size]
            else:
                print("Error in receiving contract info")

        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

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
                print(f'\nError Code: {data['code']}')
                print(f'Error Message: {data['msg']}')
                print('Please refer to the docs:')
                print('https://docs.blofin.com/index.html#errors\n')

        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

    ##################################### Calculate Size #######################################

    def calculate_size(self, size, position_side, order_type, price=None):
        balance = self.check_balance()
        [contract_value, min_size] = self.contract_info()
        size_in_usdt = round((balance * size) / 100 , 2)
        leverage_multiplier = self.leverage(position_side)
        size_with_leverage = (size_in_usdt * leverage_multiplier)
        text = lambda x: print(f"{x} Contract(s) (With leverage)")

        if price is None:
            price = self.get_market_price()[0]

        each_contract_in_usdt = (contract_value * price)
        print(f"{size}% of Balance: {size_in_usdt} USDT")
        print(f'Leverage: {leverage_multiplier}x')

        if min_size == '1' or order_type == "trigger":
            size_in_contract = math.floor(size_with_leverage / each_contract_in_usdt)
            text(size_in_contract)
            return [size_in_contract, price, size_with_leverage, leverage_multiplier]
        
        elif min_size == '0.1':
            size_in_contract = math.floor((size_with_leverage / each_contract_in_usdt) * 10 ) / 10
            text(size_in_contract)
            return [size_in_contract, price, size_with_leverage, leverage_multiplier]
            

        elif min_size == '0.01':
            size_in_contract = math.floor((size_with_leverage / each_contract_in_usdt) * 100 ) / 100
            text(size_in_contract)
            return [size_in_contract, price, size_with_leverage, leverage_multiplier]
        
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
            "ACCESS-PASSPHRASE":passphrase,
        }

        try:
            response = requests.request(method, self.url+path, headers=headers)
            data = response.json()
            
            if data['code'] == '0':
                return True
            else:
                print(f'\n- Error Code: {data['code']}')
                print(f'- Message: {data['msg']}\n')
                return False
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        
    ########################################## Info ##############################################

    def print_info(self):
        print('********************************************* IMPORTANT **********************************************************')
        print("If the actual order size in the website shows less than entered, don't worry!\nSize calculation in Blofin API is a little tricky!")
        print("For example: minimum size for bitcoin is 0.1 contract. 0.15 is not acceptable! Must be either 0.1 or 0.2")
        print("There is more! For trigger orders, contract size must be a whole number. 0.5 is not acceptable. Must be 1, 2, 3...")
        print('******************************************************************************************************************\n')
