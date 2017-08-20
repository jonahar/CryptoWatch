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
        if coin in self.wallet:
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
                 coins for which finding the value was failed, the values will be 'N/A'
        """
        res = []
        coins_values = lookup_value(self.wallet.keys())
        for coin_idx, coin_code in enumerate(self.wallet.keys()):
            addresses_amounts = lookup_address(coin_code, self.wallet[coin_code]['addresses'])
            total_coin_amount = 0
            if addresses_amounts is not None:
                # addresses whose balance was failed to retrieve is -1. sum everything except
                # failures
                for addr_amount in addresses_amounts:
                    if addr_amount > 0:
                        total_coin_amount += addr_amount

            total_coin_amount += self.wallet[coin_code]['manual_balance']
            total_coin_amount = float('%.8f' % total_coin_amount)  # truncate to maximum 8 digits
            # after point

            if coins_values[coin_idx] == ('N/A', 'N/A'):
                value_usd = 'N/A'
                value_btc = 'N/A'
            else:
                value_usd = float('%.3f' % (total_coin_amount * coins_values[coin_idx][0]))
                value_btc = float('%.8f' % (total_coin_amount * coins_values[coin_idx][1]))

            res.append([coin_code, total_coin_amount, value_usd, value_btc])

        return res

    def delete(self):
        """
        Delete all data from this wallet and delete the file from the disk.
        If later, funds are added to this wallet, it will be created again on the disk
        """
        if os.path.isfile(wallet_fullpath):
            os.remove(wallet_fullpath)
        self.wallet = {}


def lookup_address_old(coin, addresses):
    """
    this is the deprecated version of lookup_address(). This function makes a single API call for
    each address, and thus it is much slower.

    See documentation of lookup_address() , it has the exact behaviour
    """
    res = []
    base_query = 'https://multiexplorer.com/api/address_balance/fallback?' \
                 'currency=' + coin.lower() + '&address='
    for addr in addresses:
        try:
            res.append(float(requests.get(base_query + addr).json()['balance']))
        except Exception:
            res.append(-1)
    return res


def lookup_address(coin, addresses):
    """
    return the balance of given addresses of some coin

    :param coin the currency code (e.g. 'BTC' for bitcoin, 'ETH' for Ethereum, etc)
    :param addresses: a list of strings. each string is an address to look
    :return: a list of floats which correspond to the balances of the input addresses.
             If an address' balance could not be found or the address is invalid, the
             returned balance for this address is -1.
             In case of failure None is returned
    """

    if coin.upper() == 'BTC':
        query = 'https://blockchain.info/balance?active='
        for addr in addresses:
            query += addr + ','
        query = query[0:-1]  # remove the last comma. the API doesn't allow this
        try:
            dict = requests.get(query).json()
        except:
            # if at least one of the addresses is invalid the call will fail. try extracting them
            # one by one using the old lookup
            return lookup_address_old(coin, addresses)
        res = []
        for addr in dict.keys():
            amount_satoshi = float(dict[addr]['final_balance'])
            res.append(amount_satoshi / 1e8)
        return res

    if coin.upper() == 'LTC':
        query = 'http://ltc.blockr.io/api/v1/address/balance/'
        for addr in addresses:
            query += addr + ','
        coins_info = requests.get(query).json()['data']  # list of dictionaries
        res = []
        for coin_info in coins_info:
            res.append(float(coin_info['balance']))
        return res

    if coin.upper() == 'ETH':
        query = 'https://api.etherscan.io/api?module=account&action=balancemulti&address='
        for addr in addresses:
            query += addr + ','
        coins_info = requests.get(query).json()['result']  # list of dictionaries
        res = []
        for coin_info in coins_info:
            try:
                res.append(float(coin_info['balance']) / 1e18)  # amount is returned in atomic units
            except:
                res.append(-1)
        return res

    # TODO add special lookup for BCH

    return lookup_address_old(coin, addresses)


def lookup_value(coins):
    """
    return the value of the given coins in USD and BTC

    :param coins: a collection of coin codes.
    :return: list of tuples - each tuple is (coin_value_USD, coin_value_BTC).
             if a coin is not found, its tuple will be ('N/A', 'N/A')
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
                res.append(('N/A', 'N/A'))
        return res

    except Exception:
        return [('N/A', 'N/A')] * len(coins)
