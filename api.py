import requests
import json
import hmac
from hashlib import sha256
import base64
import time
import json
import uuid
import os
import datetime
from dotenv import load_dotenv
load_dotenv()

class Blofin:
    def __init__(self, symbol=""):
        self.symbol = symbol
        self.api_key = os.getenv("API_KEY")
        self.secret = os.getenv("SECRET")
        self.passphrase = os.getenv("PASSPHRASE")
        self.url = "https://openapi.blofin.com"

    ################################ GENERATE SIGNATURE ################################

    def gen_signature(self, path, method, timestamp, nonce, body={}):
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
        method = "POST"
        path = "/api/v1/account/set-leverage"
        body = {
            "instId":self.symbol,
            "leverage":leverage,
            "marginMode":self.get_margin_mode(),
            "positionSide":positionSide
        }

        if positionSide == 'both':
            both = ['long', 'short']
            for pside in both:
                try:
                    nonce = str(uuid.uuid4())
                    timestamp = int(round(time.time() * 1000))
                    body['positionSide'] = pside
                    h = self.gen_signature(path, method, timestamp, nonce, body)
                    response = requests.request(method, self.url+path, headers=h, json=body)
                    data = response.json()
                    if data['code'] == "0":
                        print('\n###########################')
                        print("Set Leverage Successfully")
                        print(f'Symbol:        {self.symbol}')
                        print(f'Leverage       {leverage}')
                        print(f'Position Side: {pside}')
                        print('###########################\n')
                        
                    else:
                        print(f'\nError Code: {data['code']}')
                        print(f'Error Message: {data['msg']}')
                        print('Please refer to the docs:')
                        print('https://docs.blofin.com/index.html#errors\n')

                except requests.exceptions.HTTPError as http_err:
                    print(f'HTTP error occurred: {http_err}')
                except Exception as err:
                    print(f'Other error occurred: {err}')
        else:
            try:
                nonce = str(uuid.uuid4())
                timestamp = int(round(time.time() * 1000))
                h = self.gen_signature(path, method, timestamp, nonce, body)
                response = requests.request(method, self.url+path, headers=h, json=body)
                data = response.json()
                if data['code'] == "0":
                    print('\n###########################')
                    print("Set Leverage Successfully")
                    print(f'Symbol:        {self.symbol}')
                    print(f'Leverage       {leverage}')
                    print(f'Position Side: {positionSide}')
                    print('###########################\n')
                    
                else:
                    print(f'\nError Code: {data['code']}')
                    print(f'Error Message: {data['msg']}')
                    print('Please refer to the docs:')
                    print('https://docs.blofin.com/index.html#errors\n')

            except requests.exceptions.HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}')
    
    ########################################## GET LEVERAGE ####################################

    def get_leverage(self, symbols):
        words = symbols.split(',')
        modified_words = [element + '-usdt' for element in words]
        modified_symbols = ','.join(modified_words)
        path = f"/api/v1/account/batch-leverage-info?instId={modified_symbols}&marginMode={self.get_margin_mode()}"
        method = "GET"
        nonce = str(uuid.uuid4())
        timestamp = int(round(time.time() * 1000))

        try:
            h = self.gen_signature(path, method, timestamp, nonce)
            res = requests.request(method, self.url+path, headers=h)
            data = res.json()
            if data['code'] == "0":
                info = data['data']
                i = 0
                while( i<len(info) -1 ):
                    print('\n###########################')
                    print(f'Symbol: {info[i]['instId']}')
                    print(f'Long;  Leverage: {info[i]['leverage']}x')
                    print(f'Short; Leverage: {info[i+1]['leverage']}x')
                    print('###########################\n')

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
            "marginMode":self.get_margin_mode(),
            "positionSide":positionSide,
            "side":side,
            "size":size,
            "orderPrice":"-1",
            "orderType":"trigger",
            "triggerPrice":price,
            "triggerPriceType": "last",
            "attachAlgoOrders":[{
                "tpTriggerPrice":tp,
                "tpOrderPrice":tp,
                "tpTriggerPriceType":"last",
                "slTriggerPrice":sl,
                "slOrderPrice":sl,
                "slTriggerPriceType":"last"
            }]
        }

        try:
            h = self.gen_signature(path, method, timestamp, nonce, body)
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
            "marginMode":self.get_margin_mode(),
            "positionSide":positionSide,
            "side":side,
            "orderType":orderType,
            "price":price,
            "size":size,
            "tpTriggerPrice": tp,
            "tpOrderPrice": tp,
            "slTriggerPrice":sl,
            "slOrderPrice": sl
        }

        if orderType == "market":
            body.pop('price')

        try:
            h = self.gen_signature(path, method, timestamp, nonce, body)
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
                        print(f'Error Message: {data['msg']}. {data['data']['msg']}\n')
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

    def cancel_order(self, order_type, id):
        if order_type == "trigger" or order_type == "t":
            path = "/api/v1/trade/cancel-algo"
            body = { "algoId": id }
        else:
            path = "/api/v1/trade/cancel-order"
            body = { "orderId": id }
        
        method = "POST"
        timestamp = int(round(time.time() * 1000))
        nonce = str(uuid.uuid4())

        try:
            h = self.gen_signature(path, method, timestamp, nonce, body)
            response = requests.request(method, self.url+path, headers=h, json=body)
            data = response.json()
            
            if data['code'] == "0":
                if order_type == "trigger":
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

    def close_position(self, positionSide):
        path = "/api/v1/trade/close-position"
        method = "POST"
        timestamp = int(round(time.time() * 1000))
        nonce = str(uuid.uuid4())

        body = {
            "instId":self.symbol,
            "marginMode":self.get_margin_mode(),
            "positionSide":positionSide,
        }

        try:
            h = self.gen_signature(path, method, timestamp, nonce, body)
            response = requests.request(method, self.url+path, headers=h, json=body)
            data = response.json()
            if data['code'] == "0":
                if positionSide == "long":
                    print(f"\n{self.symbol}; Long Position Closed\n")
                else:
                    print(f"\n{self.symbol}; Short Position Closed\n")
            else:
                print(f"\nError Code: {data['code']}")
                print(f'Error Message: "{data['msg']}"')
                print('Please refer to the docs:')
                print('https://docs.blofin.com/index.html#errors\n')
            
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

    ################################ GET OPEN TRIGGER ORDERS ###################################

    def get_open_trigger_orders(self):
        method = "GET"
        path = "/api/v1/trade/orders-algo-pending?orderType=trigger"
        nonce = str(uuid.uuid4())
        timestamp = int(round(time.time() * 1000))
        try:
            h = self.gen_signature(path, method, timestamp, nonce)
            res = requests.request(method, self.url+path, headers = h)
            data = res.json()
            if data['code'] == "0":
                info = data['data']
                if info:
                    print(f'{len(info)} Pending Trigger Order(s)')
                    for item in info:
                        print(f'\n################################################################')
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
                        print(f'################################################################\n')
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
            h = self.gen_signature(path, method, timestamp, nonce)
            res = requests.request(method, self.url+path, headers = h)
            data = res.json()
            if data['code'] == "0":
                info = data['data']
                if info:
                    print(f'{len(info)} Pending Order(s)')
                    for item in info:
                        print(f'\n################################################################')
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
                        print(f'################################################################\n')
                else:
                    print('0 Pending Orders')
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
                return float(data['data'][0]['markPrice'])
            else:
                print("Error in receiving market price")

        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
    
    #################################### GET OPEN POSITIONS ####################################

    def get_open_positions(self):
        method = "GET"
        path = "/api/v1/account/positions"
        nonce = str(uuid.uuid4())
        timestamp = int(round(time.time() * 1000))
        try:
            h = self.gen_signature(path, method, timestamp, nonce)
            res = requests.request(method, self.url+path, headers = h)
            data = res.json()
            if data['code'] == "0":
                info = data['data']
                if info:
                    print(f'{len(info)} Open Position(s)')
                    for item in info:
                        print(f'\n################################################################')
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
                        print(f'################################################################\n')
                else:
                    print('0 Open Positions')   

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
            h = self.gen_signature(path, method, timestamp, nonce)
            response = requests.request(method, self.url+path, headers=h)
            data = response.json()
            if data['code'] == "0":
                info = data['data']['details'][0]
                print('\n################################')
                print(f'Currency:        {info['currency']}')
                print(f'Total Equity:    {round(float(info['equity']), 2)}')
                print(f'Available:       {round(float(info['available']), 2)}')
                print(f'Isolated Equity: {round(float(info['isolatedEquity']), 2)}')
                print('################################\n')
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
            h = self.gen_signature(path, method, timestamp, nonce, body)
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

    def get_margin_mode(self):
        path = "/api/v1/account/margin-mode"
        method = "GET"
        timestamp = int(round(time.time() * 1000))
        nonce = str(uuid.uuid4())

        try:
            h = self.gen_signature(path, method, timestamp, nonce)
            response = requests.request(method, self.url+path, headers=h)
            data = response.json()
            if data['code'] == "0":
                print(f'\nMargin Mode: {data['data']['marginMode']}\n')
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

