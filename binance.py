import logging
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.exceptions import BinanceAPIException, BinanceOrderException
import sys

# Configure logging
logging.basicConfig(
    filename='trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.client = Client(api_key, api_secret)
        if testnet:
            self.client.API_URL = 'https://testnet.binancefuture.com/fapi/v1'
        logging.info("Initialized Binance Client for Testnet: %s", testnet)

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        """
        Place an order on Binance Futures Testnet.
        
        :param symbol: Trading pair symbol, e.g., 'BTCUSDT'
        :param side: 'BUY' or 'SELL'
        :param order_type: 'MARKET', 'LIMIT', 'STOP_LIMIT'
        :param quantity: Quantity of the asset to trade
        :param price: Price for LIMIT or STOP_LIMIT orders
        :param stop_price: Stop price for STOP_LIMIT orders
        :return: Order response dict or None if error
        """
        try:
            logging.info(f"Placing {order_type} order: {side} {quantity} {symbol} at price {price} stop_price {stop_price}")
            if order_type == 'MARKET':
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    quantity=quantity
                )
            elif order_type == 'LIMIT':
                if price is None:
                    raise ValueError("Price must be specified for LIMIT orders")
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    timeInForce='GTC',
                    quantity=quantity,
                    price=price
                )
            elif order_type == 'STOP_LIMIT':
                if price is None or stop_price is None:
                    raise ValueError("Price and stop_price must be specified for STOP_LIMIT orders")
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type=order_type,
                    timeInForce='GTC',
                    quantity=quantity,
                    price=price,
                    stopPrice=stop_price
                )
            else:
                logging.error(f"Unsupported order type: {order_type}")
                print(f"Unsupported order type: {order_type}")
                return None

            logging.info(f"Order placed successfully: {order}")
            print("Order placed successfully:")
            print(order)
            return order

        except BinanceAPIException as e:
            logging.error(f"Binance API Exception: {e}")
            print(f"Binance API Exception: {e}")
        except BinanceOrderException as e:
            logging.error(f"Binance Order Exception: {e}")
            print(f"Binance Order Exception: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            print(f"Unexpected error: {e}")
        return None

def validate_input(prompt, valid_options=None, is_float=False):
    while True:
        user_input = input(prompt).strip()
        if valid_options and user_input.upper() not in valid_options:
            print(f"Invalid input. Choose from {valid_options}")
            continue
        if is_float:
            try:
                val = float(user_input)
                if val <= 0:
                    print("Value must be positive.")
                    continue
                return val
            except ValueError:
                print("Please enter a valid number.")
                continue
        else:
            return user_input.upper()

def main():
    print("Welcome to Binance Futures Testnet Trading Bot")

    api_key = input("Enter your Binance Testnet API Key: ").strip()
    api_secret = input("Enter your Binance Testnet API Secret: ").strip()

    bot = BasicBot(api_key, api_secret, testnet=True)

    while True:
        symbol = input("Enter trading pair symbol (e.g., BTCUSDT): ").strip().upper()
        side = validate_input("Enter order side (BUY/SELL): ", valid_options=['BUY', 'SELL'])
        order_type = validate_input("Enter order type (MARKET/LIMIT/STOP_LIMIT): ", valid_options=['MARKET', 'LIMIT', 'STOP_LIMIT'])
        quantity = validate_input("Enter quantity: ", is_float=True)
        price = None
        stop_price = None

        if order_type in ['LIMIT', 'STOP_LIMIT']:
            price = validate_input("Enter price: ", is_float=True)
        if order_type == 'STOP_LIMIT':
            stop_price = validate_input("Enter stop price: ", is_float=True)

        order = bot.place_order(symbol, side, order_type, quantity, price, stop_price)

        cont = input("Place another order? (y/n): ").strip().lower()
        if cont != 'y':
            print("Exiting trading bot.")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting.")
        sys.exit(0)
