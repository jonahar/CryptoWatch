import requests
import pickle
import os

wallet_dir = os.path.join(os.path.expanduser("~"), ".cryptowatch")
wallet_filename = ".cryptowatch.wallet"
wallet_fullpath = os.path.join(wallet_dir, wallet_filename)


class Wallet:
    # self.wallet structure:
    # { coin1 : {'addresses' : {addr1, addr2, ...} , 'manual_balance' : X }
    #   coin2 : {'addresses' : {addr1, addr2, ...} , 'manual_balance' : Y } }
    #
    # the value of key 'addresses' is a set (no duplicates)

    def __init__(self):
        if not os.path.isdir(wallet_dir):
            os.mkdir(wallet_dir)
        if os.path.isfile(wallet_fullpath):
            with open(wallet_fullpath, 'rb') as f:
                self.wallet = pickle.load(f)
        else:
            self.wallet = {}

    def dump(self):
        with open(wallet_fullpath, 'wb') as f:
            pickle.dump(self.wallet, f)

    def __maybe_initialize_coin(self, coin):
        """
        prepare everything needed for a new coin in the wallet dictionary.
        That is a list of addresses to watch, and a manual balance of 0.
        If the coin already exists, does nothing.

        returns the code of the coin
        """
        coin = coin.upper()
        if coin not in self.wallet:
            coin_dict = {'addresses': set(), 'manual_balance': 0}
            self.wallet[coin] = coin_dict
        return coin

    def add_watch_address(self, coin, addresses):
        """
        add new addresses to watch

        :param coin: coin code (e.g. BTC for Bitcoin)
        :param addr: a single address as string, or a collection of addresses
        """
        if not isinstance(addresses, list):
            # a single address was given as string
            addresses = [addresses]

        coin = self.__maybe_initialize_coin(coin)

        for addr in addresses:
            self.wallet[coin]['addresses'].add(addr)

        self.dump()

    def add_manual_balance(self, coin, balance):
        """
        add balance for some coin manually. If a manual balance is already exist for this coin,
        add the given balance to the current balance

        :param coin: coin code
        :param balance: the balance to add
        """
        coin = self.__maybe_initialize_coin(coin)
        self.wallet[coin]['manual_balance'] += balance
        self.dump()

    def remove_watch_address(self, coin, addresses):
        """
        removes addresses of a coin from the watch list. If a given address is not on the watch
        list it is ignored.

        :param coin: coin code
        :param addresses: list of addresses to remove
        """
        coin = coin.upper()
        if coin.upper in self.wallet:
            for addr in addresses:
                self.wallet[coin]['addresses'].discard(addr)
        self.dump()

    def remove_manual_balance(self, coin):
        """
        removes the manual balance of the given coin
        """
        self.wallet[coin]['manual_balance'] = 0
        self.dump()

    def remove_coin(self, coin):
        """
        completely remove a coin from the wallet
        :param coin: the coin to remove
        """
        self.wallet.pop(coin, 0)
        self.dump()

    def get_coins_ids(self):
        """
        :return: list of all the coins in this wallet
        """
        return list(self.wallet.keys())

    def get_coin_info(self, coin):
        """
        :return: a dictionary with the given coin information:
                 {'addresses' : {addr1, addr2, ...} , 'manual_balance' : Y }
        """
        return self.wallet[coin]

    def get_balances(self):
        """
        :return: List of lists. each inner list has the following elements:
                      [coin_code, amount, value_in_usd, value_in_btc]
                 coins for which finding the value was failed, the values will be None
        """
        res = []
        coins_values = lookup_value(self.wallet.keys())
        for coin_idx, coin_code in enumerate(self.wallet.keys()):
            addresses_amounts = lookup_address(coin_code, self.wallet[coin_code]['addresses'])
            amount = sum(addresses_amounts)
            amount += self.wallet[coin_code]['manual_balance']

            if coins_values[coin_idx] == (None, None):
                value_usd = None
                value_btc = None
            else:
                value_usd = float('%.3f' % (amount * coins_values[coin_idx][0]))
                value_btc = float('%.8f' % (amount * coins_values[coin_idx][1]))

            res.append([coin_code, amount, value_usd, value_btc])

        return res

    def delete(self):
        """
        Delete all data from this wallet and delete the file from the disk.
        If later, funds are added to this wallet, it will be created again on the disk
        """
        if os.path.isfile(wallet_fullpath):
            os.remove(wallet_fullpath)
        self.wallet = {}


def lookup_address(coin, addresses):
    """
    return the balance of given addresses of some coin

    :param coin the currency code (e.g. 'BTC' for bitcoin, 'ETH' for Ethereum, etc)
    :param addresses: a collection of strings. each string is an address to look
    :return: a list of floats which correspond to the balances of the input addresses.
             If an address' balance could not be found or the address is invalid, the
             returned balance for this address is 0.
             In case of failure None is returned
    """
    res = []
    base_query = 'https://multiexplorer.com/api/address_balance/fallback?' \
                 'currency=' + coin.lower() + '&address='
    for addr in addresses:
        try:
            res.append(float(requests.get(base_query + addr).json()['balance']))
        except Exception:
            return None
    return res


def lookup_value(coins):
    """
    return the value of the given coins in USD and BTC

    :param coins: a collection of coin codes.
    :return: list of tuples - each tuple is (coin_value_USD, coin_value_BTC).
             if a coin is not found, its tuple contains two None's.
    """
    res = []
    try:
        all_coins = requests.get('https://api.coinmarketcap.com/v1/ticker/').json()
        for coin in coins:
            coin = coin.upper()
            found = False
            for coin_info in all_coins:
                if coin_info['symbol'] == coin:
                    # this is the coin
                    found = True
                    res.append((float(coin_info['price_usd']), float(coin_info['price_btc'])))
                    break
            if not found:
                res.append(None)
        return res

    except Exception:
        return None
